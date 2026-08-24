from schemas.analysis_result import AnalysisResult


class ResultFormatter:
    """
    Convert AnalysisResult into compact,
    LLM-readable analysis context.

    This formatter does NOT generate the final user answer.
    It only prepares structured analysis data for the LLM.
    """


    def format(
        self,
        result: AnalysisResult
    ) -> str:


        output = []


        # ==========================
        # Basic information
        # ==========================

        output.append(
            f"Ticker: {result.ticker}"
        )

        output.append(
            f"Expiration: {result.expiration}"
        )

        data_quality_report = result.data_quality_report

        if data_quality_report is not None:

            output.append(
                "\n=== DATA QUALITY ==="
            )

            output.append(
                f"Source: {data_quality_report.source}"
            )

            output.append(
                "Fetched At: "
                f"{data_quality_report.fetched_at.isoformat()}"
            )

            output.append(
                "Cache State: "
                f"{data_quality_report.cache_state}"
            )

            output.append(
                "Contract Count: "
                f"{data_quality_report.contract_count}"
            )

            for warning in data_quality_report.warnings:

                output.append(
                    "DATA QUALITY WARNING: "
                    f"{warning}"
                )


        # ==========================
        # GEX
        # ==========================

        if result.gex_result is not None:

            gex = result.gex_result

            output.append(
                "\n=== GEX ANALYSIS ==="
            )

            output.append(
                f"Total GEX: {gex.total_gex}"
            )

            output.append(
                f"Total Call GEX: {gex.call_gex}"
            )

            output.append(
                f"Total Put GEX: {gex.put_gex}"
            )


            # CALL top 3
            output.append(
                "\nCall GEX Top Levels:"
            )

            call_items = [
                gex.call_top_gex,
                gex.call_2nd_top_gex,
                gex.call_3rd_top_gex
            ]

            for index, item in enumerate(
                call_items,
                start=1
            ):

                if item is not None:

                    output.append(
                        f"{index}. "
                        f"Strike={item.strike}, "
                        f"GEX={item.gex}, "
                        f"Contract={item.contract_symbol}"
                    )


            # PUT top 3
            output.append(
                "\nPut GEX Top Levels:"
            )

            put_items = [
                gex.put_top_gex,
                gex.put_2nd_top_gex,
                gex.put_3rd_top_gex
            ]

            for index, item in enumerate(
                put_items,
                start=1
            ):

                if item is not None:

                    output.append(
                        f"{index}. "
                        f"Strike={item.strike}, "
                        f"GEX={item.gex}, "
                        f"Contract={item.contract_symbol}"
                    )


        # ==========================
        # DEX
        # ==========================

        if result.dex_result is not None:

            dex = result.dex_result

            output.append(
                "\n=== DEX ANALYSIS ==="
            )

            output.append(
                f"Call DEX: {dex.call_dex}"
            )

            output.append(
                f"Put DEX: {dex.put_dex}"
            )

            output.append(
                f"Total DEX: {dex.total_dex}"
            )


        # ==========================
        # OI
        # ==========================

        if result.oi_result is not None:

            oi = result.oi_result

            output.append(
                "\n=== OPEN INTEREST ANALYSIS ==="
            )

            output.append(
                f"DTE: {oi.dte}"
            )

            output.append(
                f"Strike Range Percent: "
                f"{oi.strike_range_percent}"
            )


            # Whole chain max OI
            if oi.call_max_oi is not None:

                output.append(
                    "\nHighest CALL OI:"
                )

                output.append(
                    f"Strike={oi.call_max_oi.strike}, "
                    f"OI={oi.call_max_oi.open_interest}, "
                    f"Contract={oi.call_max_oi.contract_symbol}"
                )


            if oi.put_max_oi is not None:

                output.append(
                    "\nHighest PUT OI:"
                )

                output.append(
                    f"Strike={oi.put_max_oi.strike}, "
                    f"OI={oi.put_max_oi.open_interest}, "
                    f"Contract={oi.put_max_oi.contract_symbol}"
                )


            # CALL top OI
            output.append(
                "\nCALL Top OI In Selected Range:"
            )

            for index, contract in enumerate(
                oi.call_top_oi,
                start=1
            ):

                output.append(
                    f"{index}. "
                    f"Strike={contract.strike}, "
                    f"OI={contract.open_interest}, "
                    f"Contract={contract.contract_symbol}"
                )


            # PUT top OI
            output.append(
                "\nPUT Top OI In Selected Range:"
            )

            for index, contract in enumerate(
                oi.put_top_oi,
                start=1
            ):

                output.append(
                    f"{index}. "
                    f"Strike={contract.strike}, "
                    f"OI={contract.open_interest}, "
                    f"Contract={contract.contract_symbol}"
                )


        # ==========================
        # Max Pain
        # ==========================

        if result.maxpain_result is not None:

            mp = result.maxpain_result

            output.append(
                "\n=== MAX PAIN ANALYSIS ==="
            )

            output.append(
                f"Max Pain Price: {mp.max_pain_price}"
            )

            output.append(
                f"Current Price: {mp.current_price}"
            )

            output.append(
                f"Distance Percent: "
                f"{mp.distance_percent}%"
            )

            output.append(
                f"Total Loss: {mp.total_loss}"
            )


        return "\n".join(output)
