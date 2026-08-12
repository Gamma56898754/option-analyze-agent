from schemas.option_chain_result import OptionChainResult
from schemas.gex_result import GEXAnalysisResult

from analysis.gex_calculation import GEXCalculator
from analysis.gex_analyzer import GEXAnalyzer



class GEXTool:
    """
    GEX analysis tool.

    Input:
        OptionChainResult

    Output:
        GEXAnalysisResult
    """


    def __init__(self):

        self.calculator = GEXCalculator()

        self.analyzer = GEXAnalyzer()



    def run(
        self,
        option_chain_result: OptionChainResult
    ) -> GEXAnalysisResult:


        # ==========================
        # 1. 获取基础数据
        # ==========================

        contracts = (
            option_chain_result.contracts
        )


        spot_price = (
            option_chain_result.underlying_price
        )


        # ==========================
        # 2. 计算单合约GEX
        # ==========================

        contract_gex_list = (
            self.calculator.calculate(
                contracts,
                spot_price
            )
        )


        # ==========================
        # 3. 汇总分析
        # ==========================

        result = (
            self.analyzer.analyze(
                contract_gex_list
            )
        )


        return result