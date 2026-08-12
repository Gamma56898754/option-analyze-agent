from schemas.option_chain_result import OptionChainResult
from schemas.oi_result import OIAnalysisResult

from analysis.oi_analyzer import OIAnalyzer


class OITool:
    """
    OI analysis tool.

    Input:
        OptionChainResult

    Output:
        OIAnalysisResult
    """


    def __init__(self):

        self.analyzer = OIAnalyzer()


    def run(
        self,
        option_chain_result: OptionChainResult
    ) -> OIAnalysisResult:
        """
        Run Open Interest analysis.

        Args:
            option_chain_result:
                Complete option chain data.

        Returns:
            OIAnalysisResult
        """


        # ==========================
        # 1. 获取分析所需数据
        # ==========================

        contracts = (
            option_chain_result.contracts
        )

        expiration_info = (
            option_chain_result.expiration_info
        )

        underlying_price = (
            option_chain_result.underlying_price
        )


        # ==========================
        # 2. OI分析
        # ==========================

        result = (
            self.analyzer.analyze(
                contracts=contracts,
                expiration_info=expiration_info,
                underlying_price=underlying_price
            )
        )


        return result