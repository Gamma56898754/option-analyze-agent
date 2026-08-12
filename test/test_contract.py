from playwright.sync_api import sync_playwright


p = sync_playwright().start()


browser = p.chromium.launch(
    headless=False
)


page = browser.new_page()


url = (
    "https://optioncharts.io/"
    "option/contract/"
    "TSLA260810C00190000"
)


page.goto(
    url,
    wait_until="networkidle"
)


print(page.title())


html = page.content()


print(
    "length:",
    len(html)
)


with open(
    "contract.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(html)


input("Enter close")


browser.close()

p.stop()