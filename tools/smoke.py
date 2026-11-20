import sys, json, re
from playwright.sync_api import sync_playwright
url="file://"+sys.argv[1]; errs=[]
with sync_playwright() as p:
    br=p.chromium.launch(headless=True, channel="chrome")
    pg=br.new_page(viewport={"width":1300,"height":850})
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(url); pg.wait_for_timeout(600)
    pg.click("#pl-table tbody tr >> nth=0"); pg.wait_for_timeout(300)
    # пауза в полёте: таблица показывает удары следующего бьющего, строка играет удар
    pg.wait_for_timeout(300); pg.click("#sc-pause"); pg.wait_for_timeout(200)
    assert pg.locator("#pl-table tbody tr").count()>0, "paused: no table rows"
    h0=pg.evaluate("()=>S.holder"); pg.click("#pl-table tbody tr >> nth=0"); pg.wait_for_timeout(5500)
    assert pg.evaluate("()=>!S.anim&&!S.paused"), "paused row click did not resume"
    print("paused-pick ok, holder", h0, "->", pg.evaluate("()=>S.holder"))
    # кнопок ударов, дублей и случайного удара больше нет; язык виден один; высота в настройках
    for sel in ["#pl-shots","#pl-status","#pl-auto","#pl-pause","#pl-rand"]: assert pg.locator(sel).count()==0, sel
    assert pg.locator(".langsw button[data-lang=ru]:visible").count()==1, "lang switch visible count"
    assert pg.locator("#settings #pl-band").count()==1
    assert pg.locator("#tabs button").count()==4
    assert pg.evaluate("()=>S.layers.side")==True, "side view default on wide screen"
    pg.click("#tabs button[data-mode=quiz]"); pg.wait_for_timeout(500)
    # поставить ждущую пару в лучшие точки и проверить, что оценка высокая.
    # В тесте №1 расставлять надо красных (ждёт удара красная пара), поэтому берём waitingTeam(), а не всегда синих,
    # и включаем вид задания «Расставить пару» (def): в других видах оценка считается иначе.
    pg.click("#qz-kinds button[data-kind=def]"); pg.wait_for_timeout(400)
    best=pg.evaluate("()=>{const t=waitingTeam();const rep=repertoire(S.holder,S.contact,S.filters);const b=optimize(t,rep,{});for(const id of MATES[t])S.pos[id]=b[id];return {kind:S.quiz.kind,team:t}}")
    pg.click("#qz-check"); pg.wait_for_timeout(400)
    qs=pg.inner_text("#qz-result").split("\n")[0]; print("quiz best:", best, qs)
    assert best["kind"]=="def" and int(qs.split()[0])>=95, "best placement must score high: "+qs
    pg.click("#qz-next"); pg.wait_for_timeout(400); pg.click("#qz-check"); pg.wait_for_timeout(400)
    print("quiz unplaced:", pg.inner_text("#qz-result").split("\n")[0])
    pg.click("#tabs button[data-mode=play]"); pg.wait_for_timeout(500)
    # перетащить синего 1 мышью
    bx=pg.evaluate("()=>{const r=document.querySelector('.pl[data-id=\"b1\"]').getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}")
    b2before=pg.evaluate("()=>({...S.pos.b2})")
    pg.mouse.move(bx[0],bx[1]); pg.mouse.down(); pg.mouse.move(bx[0]-120,bx[1]+90,steps=8); pg.mouse.up(); pg.wait_for_timeout(400)
    print("b2 before", b2before, "after", pg.evaluate("()=>S.pos.b2"))
    print("comment:", pg.inner_text("#pl-comment")[:250])
    pg.screenshot(path=sys.argv[2]+"/11-drag.png")
    # переключатель типа удара
    def at(x,y): return pg.evaluate("([x,y])=>{const pt=svg.createSVGPoint();pt.x=x;pt.y=y;const q=pt.matrixTransform(svg.getScreenCTM());return [q.x,q.y]}",[x,y])
    def drag_to(x,y,release=True):
        g=pg.evaluate("()=>{const o=grabPoint();return [o.x,o.y+o.dir*0.85]}"); s0=at(*g); e=at(x,y)
        pg.mouse.move(*s0); pg.mouse.down(); pg.mouse.move(e[0],e[1],steps=10)
        if release: pg.mouse.up()
    pg.click("#tabs button[data-mode=play]"); pg.click("#pl-reset"); pg.wait_for_timeout(400)
    names=pg.evaluate("()=>[...document.querySelectorAll('#shotsel button')].map(b=>b.dataset.t)")
    print("chips:", names); assert names==["","smash","drop","clear"], names
    d_auto=pg.evaluate("()=>Math.abs(S.pos.r2.y)")
    pg.click("#shotsel button[data-t=clear]"); pg.wait_for_timeout(800)
    d_clear=pg.evaluate("()=>Math.abs(S.pos.r2.y)")
    print("partner depth auto %.2f -> clear %.2f"%(d_auto,d_clear)); assert d_clear>d_auto+1.0, "partner must back off for a planned clear"
    card=pg.inner_text("#pl-comment"); print("card:", card[:260].replace("\n"," | ")); assert "Red 2" in card and "clear" in card.lower(), "card must say the partner prepares for the clear"
    pg.screenshot(path=sys.argv[2]+"/13-sel-clear.png")
    drag_to(-0.5,4.8); pg.wait_for_timeout(200)
    ty=pg.evaluate("()=>S.anim&&S.anim.ph.shot.type"); ld=pg.evaluate("()=>Math.abs(S.anim.ph.shot.land.y)")
    print("dragged with clear ->", ty, "lands at %.2f m"%ld); assert ty=="clear" and abs(ld-4.8)<0.05, "selected type must be played where released"
    pg.wait_for_timeout(5500)
    assert pg.evaluate("()=>S.sel")==None and pg.locator("#shotsel button.on").get_attribute("data-t")=="", "selector must return to Auto after a shot"
    # смэш, отпущенный у сетки, не долетает: красный крестик, подпись, удара нет
    pg.click("#pl-reset"); pg.wait_for_timeout(400)
    pg.click("#shotsel button[data-t=smash]"); pg.wait_for_timeout(800)
    n0=pg.evaluate("()=>S.history.length")
    drag_to(0.3,1.0,release=False); pg.wait_for_timeout(100)
    lab=pg.evaluate("()=>L.prev.textContent"); print("preview label:", lab); assert re.search("reach|долетит|sampai",lab), lab
    assert pg.evaluate("()=>!!L.prev.querySelector('path[stroke=\"#ef4444\"]')"), "red cross"
    pg.screenshot(path=sys.argv[2]+"/14-sel-bad.png")
    pg.mouse.up(); pg.wait_for_timeout(500)
    assert pg.evaluate("()=>!S.anim&&S.history.length")==n0 and pg.evaluate("()=>S.holder")=="r1", "out-of-range shot must not be played"
    assert pg.evaluate("()=>S.sel")=="smash"
    # смэш в заднюю зону: сыгран смэш (а не высоко-далёкий)
    drag_to(0.5,6.0); pg.wait_for_timeout(200)
    ty=pg.evaluate("()=>S.anim&&S.anim.ph.shot.type"); print("smash to the back ->", ty); assert ty=="smash"
    pg.wait_for_timeout(5000)
    # в уроках и тесте переключателя нет
    for m in ["lessons","quiz"]:
        pg.click("#tabs button[data-mode=%s]"%m); pg.wait_for_timeout(300)
        assert not pg.is_visible("#shotsel"), m
    pg.click("#tabs button[data-mode=play]"); pg.wait_for_timeout(300)
    assert pg.is_visible("#shotsel")
    # телефон: один переключатель языка, вид сбоку скрыт и включается галочкой
    ph=br.new_page(viewport={"width":390,"height":844})
    ph.on("pageerror", lambda e: errs.append(str(e)))
    ph.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    ph.goto(url); ph.wait_for_timeout(600)
    assert ph.locator(".langsw button[data-lang=ru]:visible").count()==1, "phone lang switch"
    assert ph.evaluate("()=>S.layers.side")==False and not ph.evaluate("()=>document.querySelector('[data-layer=side]').checked")
    ph.evaluate("()=>document.getElementById('settings').open=true")
    ph.check("[data-layer=side]"); ph.wait_for_timeout(200)
    assert ph.evaluate("()=>S.layers.side")==True
    ph.screenshot(path=sys.argv[2]+"/12-phone-side-on.png")
    # телефон: переключатель, корт и кнопки лежат друг под другом, не перекрываясь, и всё видно без прокрутки
    ph.evaluate("()=>{document.querySelector('[data-layer=side]').checked=false;document.querySelector('[data-layer=side]').dispatchEvent(new Event('change'))}")
    ph.evaluate("()=>window.scrollTo(0,0)"); ph.wait_for_timeout(300)
    r=ph.evaluate("()=>{const q=s=>{const b=document.querySelector(s).getBoundingClientRect();return [b.top,b.bottom,b.left,b.right]};return {top:q('#shotsel'),svg:q('#court'),bar:q('.stage-bar'),ctl:q('#stage-ctl'),lang:q('.stage-lang')}}")
    print("phone layout:", r)
    assert r["top"][1]<=r["svg"][0]+1 and r["svg"][1]<=r["bar"][0]+1 and r["bar"][1]<=844, "phone: nothing may lie over the court or below the screen"
    assert r["ctl"][3]<=r["lang"][2]+1, "phone: control buttons and language switch must not overlap"
    ph.screenshot(path=sys.argv[2]+"/15-phone-play.png")
    br.close()
print("ERRORS:", errs)
