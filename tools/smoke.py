import sys, json
from playwright.sync_api import sync_playwright
url="file://"+sys.argv[1]; errs=[]
with sync_playwright() as p:
    br=p.chromium.launch(headless=True, channel="chrome")
    pg=br.new_page(viewport={"width":1300,"height":850})
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(url); pg.wait_for_timeout(600)
    pg.click("#pl-shots .shotrow button >> nth=0"); pg.wait_for_timeout(300)
    pg.click("#tabs button[data-mode=quiz]"); pg.wait_for_timeout(500)   # переключение во время полёта
    # поставить синих в лучшие точки и проверить, что оценка высокая
    best=pg.evaluate("()=>{const rep=repertoire(S.holder,S.contact,S.filters);const b=optimize('blue',rep,{});S.pos.b1=b.b1;S.pos.b2=b.b2;return b}")
    pg.click("#qz-check"); pg.wait_for_timeout(400)
    print("quiz best:", pg.inner_text("#qz-result").split("\n")[0])
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
    br.close()
print("ERRORS:", errs)
