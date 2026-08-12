from dataclasses import dataclass

from schemas.option_contract import OptionContract



@dataclass
class ContractGEX:
    """
    Single option contract gamma exposure
    """

    contract_symbol: str

    option_type: str

    strike: float

    gex: float



class GEXCalculator:
    """
    Calculate OptionCharts style GEX

    Formula:

    GEX =
    Gamma
    * Open Interest
    * 100
    * Spot^2
    * 0.01
    * sign

    CALL = positive
    PUT  = negative
    """

    CONTRACT_MULTIPLIER = 100


    def calculate(
        self,
        contracts: list[OptionContract],
        spot_price: float
    ) -> list[ContractGEX]:

        results = []


        for contract in contracts:

            gex = self.calculate_contract_gex(
                contract,
                spot_price
            )


            results.append(gex)


        return results



    def calculate_contract_gex(
        self,
        contract: OptionContract,
        spot_price: float
    ) -> ContractGEX:


        if contract.gamma is None:
            gamma = 0

        else:
            gamma = contract.gamma



        if contract.open_interest is None:
            oi = 0

        else:
            oi = contract.open_interest



        raw_gex = (
            gamma
            *
            oi
            *
            self.CONTRACT_MULTIPLIER
            *
            spot_price ** 2
            *
            0.01
        )



        if contract.option_type == "CALL":

            sign = 1


        elif contract.option_type == "PUT":

            sign = -1


        else:

            raise ValueError(
                f"Unknown option type: {contract.option_type}"
            )



        final_gex = raw_gex * sign



        return ContractGEX(

            contract_symbol=
                contract.contract_symbol,

            option_type=
                contract.option_type,

            strike=
                contract.strike,

            gex=
                final_gex
        )