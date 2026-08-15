from schemas.analysis_request import AnalysisRequest



class RequestValidator:
    """
    Validate AnalysisRequest before execution.

    Responsibility:
        - validate ticker
        - validate expiration format
        - validate analysis types

    Does NOT:
        - fetch market data
        - resolve expiration
        - call tools
    """


    VALID_ANALYSIS_TYPES = {
        "gex",
        "dex",
        "oi",
        "maxpain"
    }

    VALID_EXECUTION_MODES = {
        "run_analysis",
        "explain_existing",
    }


    def validate(
        self,
        request: AnalysisRequest
    ) -> bool:
        """
        Validate user request.

        Returns:
            True if valid

        Raises:
            ValueError
        """


        # ==========================
        # 1. ticker check
        # ==========================

        if not request.ticker:

            raise ValueError(
                "Ticker cannot be empty"
            )


        if not request.ticker.isalpha():

            raise ValueError(
                f"Invalid ticker: {request.ticker}"
            )


        # ==========================
        # 2. expiration check
        # ==========================

        if not request.expiration:

            raise ValueError(
                "Expiration cannot be empty"
            )


        parts = request.expiration.split("-")


        if len(parts) != 3:

            raise ValueError(
                "Expiration format must be YYYY-MM-DD"
            )


        # ==========================
        # 3. analysis type check
        # ==========================

        if not request.analysis_types:

            raise ValueError(
                "No analysis type selected"
            )


        for analysis_type in request.analysis_types:

            if analysis_type not in self.VALID_ANALYSIS_TYPES:

                raise ValueError(
                    f"Unsupported analysis type: {analysis_type}"
                )

        if (
            request.execution_mode
            not in self.VALID_EXECUTION_MODES
        ):
            raise ValueError(
                "Unsupported execution mode: "
                f"{request.execution_mode}"
            )

        if not isinstance(
            request.force_refresh,
            bool
        ):
            raise ValueError(
                "force_refresh must be a boolean"
            )

        if (
            request.execution_mode
            == "explain_existing"
            and request.force_refresh
        ):
            raise ValueError(
                "explain_existing cannot force refresh"
            )

        return True