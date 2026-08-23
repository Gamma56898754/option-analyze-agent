"""
OptionCharts Client

Responsibility:

1. Receive browser cookies
2. Create authenticated requests session
3. Request option chain HTML
4. Request expiration overview HTML

This file DOES NOT:

- parse HTML
- create OptionContract
- calculate Greeks
- calculate GEX

"""

from core.exceptions import (
    MarketDataUnavailableError,
)
import requests



class OptionChartClient:


    BASE_URL = "https://optioncharts.io"



    def __init__(self, cookies):
        """
        Initialize client with browser cookies.

        Args:
            cookies:
                Cookies obtained from Playwright
        """


        self.session = requests.Session()


        self.session.headers.update({

            "User-Agent":
            (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/145 Safari/537.36"
            ),

            "Accept-Language":
            "zh-CN,zh;q=0.9"

        })


        self._inject_cookies(cookies)



    def _inject_cookies(self, cookies):
        """
        Copy Playwright cookies into requests session.
        """


        for cookie in cookies:

            self.session.cookies.set(

                cookie["name"],

                cookie["value"]

            )



    def get_option_chain(
        self,
        ticker: str,
        expiration: str,
        expiration_type: str
    ) -> str:
        """
        Fetch option chain HTML.


        Args:

            ticker:
                Stock symbol

            expiration:
                Expiration date

                Example:
                2026-08-21


            expiration_type:
                Option expiration type

                w:
                    weekly

                m:
                    monthly


        Returns:

            HTML response text

        """


        url = (
            f"{self.BASE_URL}"
            "/async/option_chain"
        )


        params = {


            "ticker":
                ticker,


            "option_type":
                "all",


            "view":
                "list",


            "strike_range":
                "all",


            "expiration_dates":
                f"{expiration}:{expiration_type}"


        }



        headers = {


            "HX-Request":
                "true",


            "HX-Current-URL":
                (
                    f"{self.BASE_URL}"
                    f"/options/{ticker}/option-chain"
                ),


            "Referer":
                (
                    f"{self.BASE_URL}"
                    f"/options/{ticker}/option-chain"
                )

        }



        try:

            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=10,
            )

        except requests.RequestException as exc:

            raise MarketDataUnavailableError(
                source="OptionCharts",
                operation="option_chain",
            ) from exc


        print(
            "OptionChain request:"
        )


        print(
            response.url
        )


        print(
            "Status:",
            response.status_code
        )


        print(
            "Length:",
            len(response.text)
        )

        if response.status_code != 200:

            raise MarketDataUnavailableError(
                source="OptionCharts",
                operation="option_chain",
                status_code=response.status_code,
            )


        return response.text




    def get_expiration_overview(
        self,
        ticker: str
    ) -> str:
        """
        Get ticker expiration overview HTML.

        This endpoint contains expiration metadata:

        expiration_dates=YYYY-MM-DD:w
        expiration_dates=YYYY-MM-DD:m

        """


        url = (
            self.BASE_URL +
            "/async/options_ticker_overview_live"
        )


        params = {

            "ticker": ticker

        }


        print(
            "Expiration overview request:"
        )


        print(
            url,
            params
        )


        try:

            response = self.session.get(
                url,
                params=params,
                timeout=10,
            )

        except requests.RequestException as exc:

            raise MarketDataUnavailableError(
                source="OptionCharts",
                operation="expiration_overview",
            ) from exc


        print(
            "Status:",
            response.status_code
        )


        if response.status_code != 200:

            raise MarketDataUnavailableError(
                source="OptionCharts",
                operation="expiration_overview",
                status_code=response.status_code,
            )


        html = response.text


        print(
            "Expiration HTML length:",
            len(html)
        )


        return html