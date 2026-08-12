from schemas.analysis_request import AnalysisRequest
from schemas.analysis_result import AnalysisResult


from tools.option_chain_tool import OptionChainTool
from tools.gex_tool import GEXTool
from tools.dex_tool import DEXTool
from tools.oi_tool import OITool
from tools.max_pain_tool import MaxPainTool



class AnalysisRunner:


    def __init__(
        self,
        runtime
    ):


        # ==========================
        # Data acquisition
        # ==========================

        self.option_chain_tool = OptionChainTool(
            runtime
        )


        # ==========================
        # Tool Registry
        # ==========================

        self.tools = {

            "gex": GEXTool(),

            "dex": DEXTool(),

            "oi": OITool(),

            "maxpain": MaxPainTool()

        }



    def run(
        self,
        request: AnalysisRequest
    ) -> AnalysisResult:



        # ==========================
        # 1. Get option chain
        # ==========================

        option_chain_result = (
            self.option_chain_tool.run(
                ticker=request.ticker,
                expiration_date=request.expiration
            )
        )



        # ==========================
        # 2. Create result
        # ==========================

        analysis_result = AnalysisResult(

            ticker=request.ticker,

            expiration=request.expiration

        )



        # ==========================
        # 3. Dynamic tool calling
        # ==========================

        for analysis_type in request.analysis_types:


            tool = self.tools.get(
                analysis_type
            )


            if tool is None:

                raise ValueError(
                    f"Unknown analysis type: {analysis_type}"
                )


            result = tool.run(
                option_chain_result
            )



            # ==========================
            # 4. Attach result
            # ==========================

            if analysis_type == "gex":

                analysis_result.gex_result = result


            elif analysis_type == "dex":

                analysis_result.dex_result = result


            elif analysis_type == "oi":

                analysis_result.oi_result = result


            elif analysis_type == "maxpain":

                analysis_result.maxpain_result = result



        return analysis_result