
from schemas.dex_result import DEXResult
from schemas.option_contract import OptionContract









class DEXAnalyzer:
    """
    Analyze option chain Delta Exposure.

    Input:

        list[OptionContract]


    Output:

        DEXResult


    Formula:

        DEX = Delta × Open Interest × Contract Multiplier


    Responsibility:

        OptionContract[]
                |
                ↓
            DEXResult


    Does NOT:
        - calculate option delta
        - rank contracts
        - analyze strike levels
    """



    CONTRACT_MULTIPLIER = 100



    def analyze(
        self,
        contracts: list[OptionContract]
    ) -> DEXResult:


        call_dex = 0.0

        put_dex = 0.0



        for contract in contracts:



            # Skip invalid data

            if contract.delta is None:

                continue


            if contract.open_interest is None:

                continue



            # ======================
            # Single contract DEX
            # ======================

            dex = (
                contract.delta
                *
                contract.open_interest
                *
                self.CONTRACT_MULTIPLIER
            )



            # ======================
            # Aggregate
            # ======================

            if contract.option_type == "CALL":

                call_dex += dex



            elif contract.option_type == "PUT":

                put_dex += dex




        total_dex = (
            call_dex
            +
            put_dex
        )



        return DEXResult(

            call_dex=call_dex,

            put_dex=put_dex,

            total_dex=total_dex

        )