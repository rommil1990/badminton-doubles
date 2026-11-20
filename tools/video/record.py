# Запись: ведёт браузер по сценарию, длительности фраз берёт из /tmp/badm-video/durations.json.
# Результат: /tmp/badm-video/raw/*.webm и /tmp/badm-video/timeline.json (время начала каждой фразы).
# Запуск: /Users/rommil/.local/share/pw-chrome/.venv/bin/python -I record.py
import os, sys, json, time, glob, shutil, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenario import SCENES
from cfg import TMP, LANG
from playwright.sync_api import sync_playwright
URL="file://"+os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..","docs","index.html"))
RAW=TMP+"/raw"
W,H,BAND=1280,800,72   # кадр; нижняя полоса под субтитры
GAP_PHRASE,GAP_SCENE=0.35,0.7
DURS={int(k):v for k,v in json.load(open(TMP+"/durations.json")).items()}

INIT=r"""
(()=>{
const css=document.createElement('style');
css.textContent=`#app{height:calc(100vh - %dpx)!important}
#vsub{position:fixed;left:0;right:0;bottom:0;height:%dpx;background:rgba(6,10,18,.9);color:#fff;display:flex;align-items:center;justify-content:center;
 text-align:center;font:600 27px/1.25 -apple-system,'Helvetica Neue',Arial,sans-serif;padding:0 40px;z-index:99998;box-sizing:border-box;text-shadow:0 1px 3px #000}
#vcur{position:fixed;left:0;top:0;width:34px;height:34px;margin:-17px 0 0 -17px;border-radius:50%%;background:rgba(255,214,0,.35);border:3px solid #ffd600;
 box-shadow:0 0 0 2px rgba(0,0,0,.55),0 2px 8px rgba(0,0,0,.6);pointer-events:none;z-index:99999;transition:transform .12s;display:none}
#vcur::after{content:'';position:absolute;left:11px;top:11px;width:6px;height:6px;border-radius:50%%;background:#000}
#vcur.down{transform:scale(.6);background:rgba(255,80,0,.55);border-color:#ff5a1f}
#vcur.ring{animation:vp .5s ease-out}
@keyframes vp{0%%{box-shadow:0 0 0 2px rgba(0,0,0,.55),0 0 0 0 rgba(255,214,0,.9)}100%%{box-shadow:0 0 0 2px rgba(0,0,0,.55),0 0 0 26px rgba(255,214,0,0)}}`;
const add=()=>{
 document.head.appendChild(css);
 const s=document.createElement('div');s.id='vsub';document.body.appendChild(s);
 const c=document.createElement('div');c.id='vcur';document.body.appendChild(c);
 addEventListener('pointermove',e=>{c.style.display='block';c.style.left=e.clientX+'px';c.style.top=e.clientY+'px'},true);
 addEventListener('pointerdown',()=>{c.classList.add('down');c.classList.remove('ring');void c.offsetWidth;c.classList.add('ring')},true);
 addEventListener('pointerup',()=>{c.classList.remove('down')},true);
};
if(document.body)add();else addEventListener('DOMContentLoaded',add);
})();
""" % (BAND,BAND)

class Ctx:
    def __init__(s,pg): s.pg=pg; s.x=900; s.y=300; s.t0=0; s.dur=0
    def sleep(s,t): time.sleep(max(0,t))
    def until(s,frac): s.sleep(s.t0+frac*s.dur-time.time())
    def move(s,x,y,dur=0.7):
        n=max(4,int(dur*45)); x0,y0=s.x,s.y
        for i in range(1,n+1):
            k=i/n; k=k*k*(3-2*k)
            s.pg.mouse.move(x0+(x-x0)*k,y0+(y-y0)*k); time.sleep(dur/n)
        s.x,s.y=x,y
    def ctr(s,sel,nth=0):
        b=s.pg.locator(sel).nth(nth).bounding_box(); return b["x"]+b["width"]/2,b["y"]+b["height"]/2
    def goto(s,sel,nth=0,dur=0.7): x,y=s.ctr(sel,nth); s.move(x,y,dur); return x,y
    def click(s,sel,nth=0,dur=0.7):
        s.goto(sel,nth,dur); s.goto(sel,nth,0.15); s.sleep(0.1); s.pg.mouse.down(); s.sleep(0.12); s.pg.mouse.up(); s.sleep(0.2)
    def svgpt(s,x,y): return s.pg.evaluate("([x,y])=>{const pt=svg.createSVGPoint();pt.x=x;pt.y=y;const q=pt.matrixTransform(svg.getScreenCTM());return [q.x,q.y]}",[x,y])
    def grab(s): return s.pg.evaluate("()=>{const o=grabPoint();return [o.x,o.y+o.dir*0.85]}")
    def idle(s,mx=9):
        s.pg.wait_for_function("()=>!S.anim",timeout=int(mx*1000))
    def reset(s):
        s.idle(); s.pg.evaluate("()=>document.getElementById('pl-reset').click()"); s.sleep(0.5)
    def drag_shuttle(s,x,y,release=True,dur=1.1):
        g=s.svgpt(*s.grab()); e=s.svgpt(x,y)
        s.move(*g,dur=0.8); s.pg.mouse.down(); s.sleep(0.15); s.move(*e,dur=dur)
        if release: s.sleep(0.2); s.pg.mouse.up()
    def drag_player(s,pid,x,y,dur=1.0):
        a=s.ctr(f'.pl[data-id="{pid}"]'); e=s.svgpt(x,y)
        s.move(*a,dur=0.7); s.pg.mouse.down(); s.sleep(0.12); s.move(*e,dur=dur); s.sleep(0.15); s.pg.mouse.up(); s.sleep(0.4)
    def waiting_first(s): return s.pg.evaluate("()=>MATES[waitingTeam()][0]")

# ---------- действия ----------
def intro_court(c):
    c.goto("svg#court",dur=0.9); x,y=c.svgpt(0,5); c.move(x,y,1.2); c.until(.55); x,y=c.svgpt(0,-5); c.move(x,y,1.5)
def tabs_hover(c):
    for i in range(4):
        c.goto("#tabs button",i,0.5); c.sleep(0.35)
def lang_switch(c):
    # switch through the other languages and finish on the video language
    seq=[l for l in ("ru","en") if l!=LANG]+["id",LANG]
    for i,l in enumerate(seq):
        c.click("#panel .langsw button[data-lang=%s]"%l)
        if i<len(seq)-1: c.until((.5,.75)[i])
def to_card(c): c.goto("#pl-comment",dur=1.0)
def table_cols(c):
    c.goto("#pl-table th",0,0.8); c.until(.35); c.goto("#pl-table th",1,1.2); 
def table_dots(c):
    c.goto("#pl-table th",2,0.6); c.until(.4); x,y=c.ctr("#pl-table tbody tr",0); c.move(x-80,y,0.8)
    c.until(.7); x,y=c.ctr("#pl-table tbody tr",3); c.move(x-80,y,1.0)
def table_hover(c):
    for i in (1,4,6):
        c.goto("#pl-table tbody tr",i,0.7); c.sleep(0.9)
def way_row(c):
    c.click("#pl-table tbody tr",0,0.9); c.idle(9)
def way_dot(c):
    c.sleep(0.3); x,y=c.ctr(".tgt",2); c.move(x,y,1.0); c.sleep(0.2); c.pg.mouse.down(); c.sleep(0.12); c.pg.mouse.up(); c.idle(9)
def way_drag(c):
    # тянем волан к сетке (укороченный) - но отпускаем в следующей фразе
    c.sleep(0.3); s=c.pg.evaluate("()=>sideOf(teamOf(S.holder))")  # сторона бьющего
    c.dsy=-s  # половина соперника
    c.drag_shuttle(0.2,c.dsy*2.0,release=False,dur=1.3)
def way_drag2(c):
    c.sleep(0.8); c.pg.mouse.up(); c.idle(9); c.sleep(0.5)
    s=c.pg.evaluate("()=>sideOf(teamOf(S.holder))"); c.drag_shuttle(0.8,-s*5.2,dur=1.2); c.idle(9)
def type_clear(c):
    c.reset(); c.click("#shotsel button[data-t=clear]"); c.until(.9)
def type_smash_bad(c):
    c.reset(); c.click("#shotsel button[data-t=smash]"); c.sleep(0.5)
    s=c.pg.evaluate("()=>sideOf(teamOf(S.holder))"); c.drag_shuttle(0.3,-s*1.0,release=False,dur=1.0)
def type_smash_ok(c):
    c.sleep(1.2); c.pg.mouse.up(); c.sleep(0.8)
    s=c.pg.evaluate("()=>sideOf(teamOf(S.holder))"); c.drag_shuttle(0.5,-s*5.6,dur=1.0); c.until(.62)
    c.idle(9); c.click("#shotsel button[data-t='']")
def auto_on(c):
    c.reset(); c.click("#sc-auto"); c.until(.97)
def pause_pick(c):
    c.sleep(0.8); c.click("#sc-pause"); c.until(.55); c.click("#pl-table tbody tr",1,0.9)
def drag_player(c):
    c.pg.evaluate("()=>{S.auto=false}"); c.idle(9); c.reset()
    p=c.waiting_first(); pos=c.pg.evaluate("(p)=>S.pos[p]",p)
    c.drag_player(p,pos["x"]+1.2,pos["y"]*0.55); c.sleep(0.5)
def relax(c):
    ideal=c.pg.evaluate("()=>S.ideal"); p=c.waiting_first()
    c.until(.3); c.click("#pl-relax"); 
def tips_on(c):
    c.reset(); c.click("#pl-tips")
def tip_bad(c):
    sd=c.pg.evaluate("()=>sideOf(waitingTeam())"); p=c.waiting_first()
    c.drag_player(p,0.3,sd*0.7); c.until(.97)
def tip_good(c):
    c.pg.mouse.click(5,5) if False else None
    c.reset(); ideal=c.pg.evaluate("()=>S.ideal"); p=c.waiting_first()
    c.drag_player(p,ideal[p]["x"],ideal[p]["y"]); c.until(.97)
def back_reset(c):
    c.pg.evaluate("()=>{S.tips=false;updatePanel()}") if False else None
    c.click("#pl-table tbody tr",0,0.7); c.idle(9); c.sleep(0.3)
    c.click("#pl-back",0,0.7); c.sleep(0.9); c.click("#pl-reset",0,0.7)
def show_lessons(c):
    c.click("#tabs button[data-mode=lessons]"); c.sleep(0.3); c.goto("#ls-list > *",1,0.9)
def show_quiz(c):
    c.click("#tabs button[data-mode=quiz]"); c.until(.3); c.goto("#qz-check",dur=0.8)
    c.until(.65); c.goto("#qz-grid > *",14,1.0); c.sleep(0.4); c.goto("#qz-grid > *",58,1.0)
def show_help(c):
    c.click("#tabs button[data-mode=help]"); c.sleep(0.5); c.move(1000,420,0.8)
    c.pg.evaluate("()=>document.getElementById('panel').scrollTo({top:700,behavior:'smooth'})")
def finish(c):
    c.pg.evaluate("()=>document.getElementById('panel').scrollTo(0,0)")
    c.click("#tabs button[data-mode=play]"); c.until(.7); c.goto("svg#court",dur=1.0)

ACTS={k:v for k,v in globals().items() if callable(v) and k not in ("Ctx",)}

def main():
    shutil.rmtree(RAW,ignore_errors=True); os.makedirs(RAW)
    tl=[]; errs=[]
    with sync_playwright() as p:
        br=p.chromium.launch(headless=True,channel="chrome")
        ctx=br.new_context(viewport={"width":W,"height":H},locale="ru-RU" if LANG=="ru" else "en-US",record_video_dir=RAW,record_video_size={"width":W,"height":H})
        ctx.add_init_script("try{localStorage.setItem('badm-lang','%s')}catch(e){}"%LANG)
        ctx.add_init_script(INIT)
        pg=ctx.new_page(); T0=time.time()
        pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(1200)
        c=Ctx(pg); n=0
        for si,(sid,phrases) in enumerate(SCENES):
            for text,act in phrases:
                c.t0=time.time(); c.dur=DURS[n]
                pg.evaluate("t=>{document.getElementById('vsub').textContent=t}",text)
                tl.append({"n":n,"scene":sid,"start":c.t0-T0,"dur":DURS[n],"text":text,"act":act})
                if act:
                    try: ACTS[act](c)
                    except Exception as e: print("ACT FAIL",act,str(e)[:300]); errs.append(act+": "+str(e)[:200])
                    over=time.time()-c.t0-DURS[n]
                    if over>0: print("overrun %.1fs in %s"%(over,act))
                c.sleep(c.t0+DURS[n]+GAP_PHRASE-time.time()); n+=1
            c.sleep(GAP_SCENE-GAP_PHRASE)
            if sid=="intro": pass
        pg.evaluate("()=>{document.getElementById('vsub').textContent=''}"); time.sleep(1.0)
        total=time.time()-T0
        pg.screenshot(path=TMP+"/last.png")
        ctx.close(); br.close()
    json.dump({"timeline":tl,"total":total},open(TMP+"/timeline.json","w"),ensure_ascii=False,indent=1)
    v=glob.glob(RAW+"/*.webm")[0]; os.rename(v,RAW+"/rec.webm")
    print("recorded %.1f s; errors:"%total,errs)
main()
