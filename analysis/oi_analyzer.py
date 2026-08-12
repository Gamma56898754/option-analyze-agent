from schemas.option_contract import OptionContract

from schemas.expiration_info import ExpirationInfo
from schemas.oi_result import OIAnalysisResult



class OIAnalyzer:
    """
    Analyze option chain open interest.

    Responsibilities:

    1. Select strike range based on DTE
    2. Find highest OI contracts
    3. Rank CALL and PUT OI


    Does NOT:

    - calculate DTE
    - calculate GEX
    - calculate DEX
    - analyze market direction
    """



    def analyze(
        self,
        contracts: list[OptionContract],
        expiration_info: ExpirationInfo,
        underlying_price: float
    ) -> OIAnalysisResult:


        # Step 1:
        # Read DTE from expiration metadata

        dte = expiration_info.dte



        # Step 2:
        # Select strike range

        strike_range_percent = (
            self.get_strike_range(dte)
        )



        # Step 3:
        # Find max OI from whole chain

        call_max_oi = self.get_max_oi(
            contracts,
            "CALL"
        )


        put_max_oi = self.get_max_oi(
            contracts,
            "PUT"
        )



        # Step 4:
        # Filter strike range

        filtered_contracts = self.filter_by_price_range(
            contracts,
            underlying_price,
            strike_range_percent
        )



        # Step 5:
        # Rank top OI inside range

        call_top_oi = self.get_top_oi(
            filtered_contracts,
            "CALL",
            3
        )


        put_top_oi = self.get_top_oi(
            filtered_contracts,
            "PUT",
            3
        )



        return OIAnalysisResult(

            dte=dte,

            strike_range_percent=strike_range_percent,

            call_max_oi=call_max_oi,

            put_max_oi=put_max_oi,

            call_top_oi=call_top_oi,

            put_top_oi=put_top_oi

        )



    def get_strike_range(
        self,
        dte: int
    ) -> float:

        """
        Decide strike range by DTE.
        """


        if dte <= 7:

            return 0.15


        elif dte <= 30:

            return 0.30


        else:

            return 0.50



    def filter_by_price_range(
        self,
        contracts: list[OptionContract],
        price: float,
        range_percent: float
    ) -> list[OptionContract]:

        lower = price * (
            1 - range_percent
        )


        upper = price * (
            1 + range_percent
        )


        return [

            contract

            for contract in contracts

            if lower
            <= contract.strike
            <= upper

        ]



    def get_max_oi(
        self,
        contracts: list[OptionContract],
        option_type: str
    ) -> OptionContract:


        matched = [

            contract

            for contract in contracts

            if contract.option_type == option_type

        ]


        return max(
            matched,
            key=lambda x: x.open_interest
        )



    def get_top_oi(
        self,
        contracts: list[OptionContract],
        option_type: str,
        limit: int
    ) -> list[OptionContract]:


        matched = [

            contract

            for contract in contracts

            if contract.option_type == option_type

        ]


        return sorted(
            matched,
            key=lambda x: x.open_interest,
            reverse=True
        )[:limit]