from playwright.sync_api import sync_playwright


url = (
    "https://optioncharts.io/options/"
    "TSLA/option-chain?"
    "option_type=all&"
    "expiration_dates=2026-08-10:w&"
    "view=list&"
    "strike_range=all"
)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )


    context = browser.new_context()


    page = context.new_page()


    print("Opening page...")


    page.goto(
        url,
        wait_until="networkidle"
    )


    print("Page loaded")


    cookies = context.cookies()


    print("\nCookies:")
    

    for cookie in cookies:

        print(
            cookie["name"],
            "=",
            cookie["value"][:50]
        )


    input("\nPress ENTER to close...")


    browser.close()