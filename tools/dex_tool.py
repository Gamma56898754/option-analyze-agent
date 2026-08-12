from schemas.option_chain_result import OptionChainResult
from schemas.dex_result import DEXResult

from analysis.dex_analyzer import DEXAnalyzer



class DEXTool:
    """
    DEX analysis tool.

    Input:
        OptionChainResult

    Output:
        DEXResult
    """


    def __init__(self):

        self.analyzer = DEXAnalyzer()



    def run(
        self,
        option_chain_result: OptionChainResult
    ) -> DEXResult:
        """
        Run DEX analysis.

        Args:
            option_chain_result:
                Complete option chain data

        Returns:
            DEXResult
        """


        contracts = (
            option_chain_result.contracts
        )


        result = (
            self.analyzer.analyze(
                contracts
            )
        )


        return result