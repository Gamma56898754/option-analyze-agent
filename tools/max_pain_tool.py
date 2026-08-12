from schemas.option_chain_result import OptionChainResult
from schemas.max_pain_result import MaxPainResult

from analysis.max_pain_analyzer import MaxPainAnalyzer



class MaxPainTool:
    """
    Max Pain analysis tool.

    Input:
        OptionChainResult

    Output:
        MaxPainResult
    """


    def __init__(self):

        self.analyzer = MaxPainAnalyzer()



    def run(
        self,
        option_chain_result: OptionChainResult
    ) -> MaxPainResult:
        """
        Run max pain calculation.

        Args:
            option_chain_result:
                Complete option chain data

        Returns:
            MaxPainResult
        """


        contracts = (
            option_chain_result.contracts
        )


        current_price = (
            option_chain_result.underlying_price
        )


        result = (
            self.analyzer.analyze(
                contracts=contracts,
                current_price=current_price
            )
        )


        return result