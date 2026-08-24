from schemas.analysis_request import AnalysisRequest
from schemas.analysis_result import AnalysisResult
import time
from core.trace import log_trace_event

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

    @staticmethod
    def _trace(
        trace_id: str | None,
        event: str,
        **fields,
    ) -> None:

        if trace_id is None:
            return

        log_trace_event(
            trace_id=trace_id,
            event=event,
            **fields,
        )

    def run(
        self,
        request: AnalysisRequest,
        trace_id: str | None = None,
    ) -> AnalysisResult:



        # ==========================
        # 1. Get option chain
        # ==========================

        (
            option_chain_result,
            data_quality_report,
        ) = self.option_chain_tool.run_with_data_quality(
            ticker=request.ticker,
            expiration_date=request.expiration,
            force_refresh=request.force_refresh,
            trace_id=trace_id,
        )



        # ==========================
        # 2. Create result
        # ==========================

        analysis_result = AnalysisResult(

            ticker=request.ticker,

            expiration=request.expiration,
            data_quality_report=data_quality_report,

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


            calculation_started_at = time.perf_counter()

            self._trace(
                trace_id,
                "analysis_calculation_started",
                analysis_type=analysis_type,
            )

            try:
                result = tool.run(
                    option_chain_result
                )

            except Exception as exc:

                self._trace(
                    trace_id,
                    "analysis_calculation_failed",
                    analysis_type=analysis_type,
                    error_type=type(exc).__name__,
                    duration_ms=round(
                        (
                            time.perf_counter()
                            - calculation_started_at
                        ) * 1000,
                        2,
                    ),
                )
                raise

            self._trace(
                trace_id,
                "analysis_calculation_completed",
                analysis_type=analysis_type,
                duration_ms=round(
                    (
                        time.perf_counter()
                        - calculation_started_at
                    ) * 1000,
                    2,
                ),
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
