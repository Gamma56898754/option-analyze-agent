from playwright.sync_api import sync_playwright
import requests


PAGE_URL = (
    "https://optioncharts.io/options/"
    "TSLA/option-chain?"
    "option_type=all&"
    "expiration_dates=2026-08-10:w&"
    "view=list&"
    "strike_range=all"
)


API_URL = (
    "https://optioncharts.io/"
    "async/option_chain"
)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )


    context = browser.new_context()


    page = context.new_page()


    print("Open page...")


    page.goto(
        PAGE_URL,
        wait_until="networkidle"
    )


    print("Browser loaded")


    # 获取cookies

    cookies = context.cookies()


    session = requests.Session()


    for cookie in cookies:

        session.cookies.set(
            cookie["name"],
            cookie["value"]
        )


    print("\nInjected cookies:")

    print(session.cookies)


    params = {

        "ticker":"TSLA",

        "option_type":"all",

        "view":"list",

        "strike_range":"all",

        "expiration_dates":
            "2026-08-10:w"

    }


    headers = {

        "HX-Request":
            "true",

        "Referer":
            PAGE_URL,

        "User-Agent":
            (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64)"
            )

    }


    response = session.get(

        API_URL,

        params=params,

        headers=headers,

        timeout=10

    )


    print("\nResponse:")

    print(
        response.status_code
    )

    print(
        "Length:",
        len(response.text)
    )


    print(
        response.text[:500]
    )


    input(
        "Press ENTER close"
    )


    browser.close()