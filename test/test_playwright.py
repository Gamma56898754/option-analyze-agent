from playwright.sync_api import sync_playwright


p = sync_playwright().start()


browser = p.chromium.launch(
    headless=False
)


page = browser.new_page()


page.goto(
    "https://optioncharts.io/options/TSLA/option-chain",
    wait_until="networkidle"
)


html = page.content()


with open(
    "optionchain.html",
    "w",
    encoding="utf-8"
) as f:

    f.write(html)


print(
    "HTML saved:",
    len(html)
)


input("Press ENTER to close...")


browser.close()

p.stop()