from data.browser_session import BrowserSession
from data.optionchart_client import OptionChartClient


class Runtime:
    """
    Application runtime.

    Responsible for managing long-lived resources:
    - browser session
    - cookies
    - option chart client
    """


    def __init__(self):

        self.browser_session = BrowserSession()

        self.client = None

        self._initialize_client()



    def _initialize_client(self):
        """
        Initialize OptionChartClient once.
        """

        print(
            "Initializing browser session..."
        )


        cookies = (
            self.browser_session
            .get_cookies()
        )


        print(
            "Cookies obtained:",
            len(cookies)
        )


        self.client = OptionChartClient(
            cookies
        )


        print(
            "OptionChartClient initialized"
        )