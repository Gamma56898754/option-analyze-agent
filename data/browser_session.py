from playwright.sync_api import sync_playwright


class BrowserSession:
    """
    Responsible for creating browser session
    and obtaining OptionCharts cookies.

    The cookie is used for accessing OptionCharts API.
    It is not bound to any specific ticker.
    """


    def __init__(self):

        self.cookies = None



    def get_cookies(self):
        """
        Open OptionCharts page once
        and obtain cookies.

        Returns:
            cookies list
        """


        # 这里只是用于建立OptionCharts访问权限
        # 不代表实际分析标的
        bootstrap_url = (
            "https://optioncharts.io"
        )


        with sync_playwright() as p:


            browser = p.chromium.launch(
                headless=True
            )


            context = browser.new_context()


            page = context.new_page()


            print(
                "Opening:",
                bootstrap_url
            )


            page.goto(
                bootstrap_url,
                wait_until="networkidle"
            )


            print(
                "Page loaded"
            )


            self.cookies = context.cookies()


            browser.close()


        return self.cookies