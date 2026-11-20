# Прогон интерфейса в headless Chrome: ошибки консоли + снимки.
import sys, time, json
from playwright.sync_api import sync_playwright
url = "file://" + sys.argv[1]
out = sys.argv[2]
errs = []
with sync_playwright() as p:
    try:
        br = p.chromium.launch(headless=True, channel="chrome")
    except Exception:
        br = p.chromium.launch(headless=True)
    pg = br.new_page(viewport={"width": 1400, "height": 900})
    pg.on("console", lambda m: (errs.append(("console", m.type, m.text)), print("CONSOLE", m.type, m.text, flush=True)) if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: (errs.append(("pageerror", str(e))), print("PAGEERROR", e, flush=True)))
    pg.goto(url); pg.wait_for_timeout(800)
    pg.screenshot(path=f"{out}/01-start.png")
    print("card:", pg.inner_text("#pl-comment"))
    # сыграть смэш по линии
    pg.click("#pl-table tbody tr >> nth=0"); pg.wait_for_timeout(500)
    pg.screenshot(path=f"{out}/02-mid-anim.png")
    pg.wait_for_timeout(2500)
    pg.screenshot(path=f"{out}/03-after.png")
    print("comment:", pg.inner_text("#pl-comment")[:600])
    # перетащить синего игрока
    box = pg.evaluate("""()=>{const g=document.querySelector('.pl[data-id="b1"]').getBoundingClientRect();return [g.x+g.width/2,g.y+g.height/2]}""")
    print("b1 at", box)
    # авторозыгрыш несколько секунд
    pg.click("#sc-auto"); pg.wait_for_timeout(9000); pg.click("#sc-auto"); pg.wait_for_timeout(2500)
    pg.screenshot(path=f"{out}/04-auto.png")
    # уроки
    pg.click("#tabs button[data-mode=lessons]"); pg.wait_for_timeout(500)
    pg.click("#ls-list button >> nth=0"); pg.wait_for_timeout(500)
    for i in range(4):
        pg.click("#ls-next"); pg.wait_for_timeout(4200)
    pg.screenshot(path=f"{out}/05-lesson1-end.png")
    print("lesson:", pg.inner_text("#ls-text")[:300], "|", pg.inner_text("#ls-step"))
    for li in range(1, 7):
        pg.click("#ls-exit"); pg.wait_for_timeout(300)
        pg.click(f"#ls-list button >> nth={li}"); pg.wait_for_timeout(400)
        n = 0
        while not pg.is_disabled("#ls-next") and n < 8:
            pg.click("#ls-next"); pg.wait_for_timeout(4500); n += 1
        print(f"lesson {li+1}: steps {n}, step label {pg.inner_text('#ls-step')}")
    pg.screenshot(path=f"{out}/06-lesson-last.png")
    # тест
    pg.click("#tabs button[data-mode=quiz]"); pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/07-quiz.png")
    pg.click("#qz-check"); pg.wait_for_timeout(600)
    pg.screenshot(path=f"{out}/08-quiz-check.png")
    print("quiz:", pg.inner_text("#qz-result")[:300])
    # мобильный
    m = br.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    m.on("pageerror", lambda e: errs.append(("pageerror-mobile", str(e))))
    m.goto(url); m.wait_for_timeout(800)
    m.screenshot(path=f"{out}/09-mobile.png")
    m.screenshot(path=f"{out}/10-mobile-full.png", full_page=True)
    br.close()
print("ERRORS:", json.dumps(errs, ensure_ascii=False, indent=1))
