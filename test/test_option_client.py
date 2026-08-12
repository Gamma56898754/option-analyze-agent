from data.browser_session import BrowserSession
from data.optionchart_client import OptionChartClient



# 1. Get cookie

browser = BrowserSession()


cookies = browser.get_cookies(
    "TSLA"
)



print("\nCookies received:")
print(cookies)



# 2. Create client

client = OptionChartClient(
    cookies
)



# 3. Fetch option chain


html = client.get_option_chain(

    ticker="TSLA",

    expiration="2026-08-10"

)



print("\nHTML preview:")

print(
    html[:500]
)