import re

from bs4 import BeautifulSoup

from schemas.option_contract import OptionContract


class OptionChainParser:
    """
    Parse OptionCharts option chain HTML.

    Responsibility:
    HTML
        ↓
    OptionContract objects

    Does NOT:
    - request webpage
    - save data
    - calculate GEX
    """



    def parse(
        self,
        html: str,
        ticker: str,
        expiration: str
    ) -> list[OptionContract]:
        """
        Parse option chain HTML.

        Args:
            html:
                Raw HTML from OptionCharts

            ticker:
                Stock symbol

            expiration:
                Expiration date

        Returns:
            List of OptionContract
        """

        soup = BeautifulSoup(
            html,
            "html.parser"
        )


        contracts = []


        # Find all table rows
        rows = soup.find_all("tr")


        for row in rows:


            contract = self.parse_row(
                row,
                ticker,
                expiration
            )


            if contract:

                contracts.append(contract)



        return contracts




    def parse_row(
        self,
        row,
        ticker,
        expiration
    ):
        """
        Parse single <tr>
        """


        # Find contract link

        link = row.find(
            "a",
            href=True
        )


        if not link:
            return None



        href = link["href"]


        if "/option/contract/" not in href:

            return None



        contract_symbol = (
            href.split("/")
            [-1]
        )



        # Extract all td values

        cells = row.find_all("td")


        values = [

            cell.get_text(
                strip=True
            )

            for cell in cells

        ]



        # Need 12 columns

        if len(values) != 12:
            

            return None



        return self.create_contract(

            values,

            contract_symbol,

            ticker,

            expiration

        )




    def create_contract(
        self,
        values,
        contract_symbol,
        ticker,
        expiration
    ):

        """
        Convert raw strings
        into OptionContract
        """



        symbol_info = self.parse_symbol(
        contract_symbol
        )
        
        option_type = symbol_info["option_type"]

        strike = symbol_info["strike"]
        


        return OptionContract(

            ticker=ticker,

            contract_symbol=
                contract_symbol,

            expiration=
                expiration,

            option_type=
                option_type,

            strike=
                strike,


            last=
                self.to_float(values[1]),

            bid=
                self.to_float(values[2]),

            mid=
                self.to_float(values[3]),

            ask=
                self.to_float(values[4]),


            volume=
                self.to_int(values[5]),

            open_interest=
                self.to_int(values[6]),


            implied_volatility=
                self.parse_percent(
                    values[7]
                ),


            delta=
                self.to_float(values[8]),

            gamma=
                self.to_float(values[9]),

            theta=
                self.to_float(values[10]),

            vega=
                self.to_float(values[11])
        
        )



    def parse_symbol(
        self,
        symbol
    ):

        """
        Parse OCC option symbol.

        Examples:

        TSLA260810C00330000

        SNDK260814C01435000

        SMR260814P00100000

        """



        pattern = (
            r"^(.+)"
            r"(\d{6})"
            r"([CP])"
            r"(\d{8})$"
        )


        match = re.match(
            pattern,
            symbol
        )


        if not match:

            raise ValueError(
                f"Invalid option symbol: {symbol}"
            )



        ticker = match.group(1)

        expiration_code = match.group(2)

        option_type_code = match.group(3)

        strike_code = match.group(4)



        # OCC strike price
        # last 8 digits / 1000

        strike = (
            int(strike_code)
            /
            1000
        )



        if option_type_code == "C":

            option_type = "CALL"


        elif option_type_code == "P":

            option_type = "PUT"


        else:

            raise ValueError(
                f"Unknown option type: {symbol}"
            )



        return {

            "ticker": ticker,

            "expiration_code": expiration_code,

            "option_type": option_type,

            "strike": strike

        }



    def to_float(
        self,
        value
    ):

        if value in ["-", ""]:

            return None

        return float(
            value.replace(
                ",",
                ""
            )
        )



    def to_int(
        self,
        value
    ):

        if value in ["-", ""]:

            return None

        return int(
            value.replace(
                ",",
                ""
            )
        )



    def parse_percent(
        self,
        value
    ):

        if value in ["-", ""]:

            return None


        cleaned_value = (
            value
            .replace("%", "")
            .replace(",", "")
        )


        return (
            float(cleaned_value)
            /
            100
        )

    def parse_underlying_price(
        self,
        html: str
    ):

        pattern = r"underlyingPrice:\s*([\d.]+)"

        match = re.search(
            pattern,
            html
        )

        if match:
            return float(
                match.group(1)
            )

        return None