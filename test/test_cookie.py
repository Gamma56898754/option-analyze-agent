from data.browser_session import BrowserSession



session = BrowserSession()



cookies = session.get_cookies(
    "TSLA"
)



print("\nCookies:")


for cookie in cookies:

    print(
        cookie["name"],
        "=",
        cookie["value"][:50]
    )