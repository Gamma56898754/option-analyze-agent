import json

from agent.result_formatter import ResultFormatter
from core.analysis_runner import AnalysisRunner
from core.request_validator import RequestValidator
from schemas.analysis_request import AnalysisRequest


class OptionToolExecutor:

    TOOL_NAME = "run_option_analysis"

    REQUIRED_ARGUMENTS = {
        "ticker",
        "expiration",
        "analysis_types",
    }

    OPTIONAL_ARGUMENTS = {
        "force_refresh",
    }

    def __init__(
        self,
        runner: AnalysisRunner,
        validator: RequestValidator,
        formatter: ResultFormatter,
    ):

        self.runner = runner

        self.validator = validator

        self.formatter = formatter

    def execute(
        self,
        tool_name: str,
        arguments_json: str,
        trace_id: str | None = None,
    ) -> dict:

        if tool_name != self.TOOL_NAME:

            raise ValueError(
                f"Unsupported tool: {tool_name}"
            )

        arguments = self._parse_arguments(
            arguments_json
        )

        request = self._build_request(
            arguments
        )

        self.validator.validate(
            request
        )

        analysis_result = self.runner.run(
            request,
            trace_id=trace_id,
        )

        analysis_context = self.formatter.format(
            analysis_result
        )

        return {
            "request": request,
            "analysis_result": analysis_result,
            "analysis_context": analysis_context,
        }

    def _parse_arguments(
        self,
        arguments_json: str,
    ) -> dict:

        try:

            arguments = json.loads(
                arguments_json
            )

        except json.JSONDecodeError as error:

            raise ValueError(
                "Tool arguments must be valid JSON"
            ) from error

        if not isinstance(
            arguments,
            dict,
        ):

            raise ValueError(
                "Tool arguments must be a JSON object"
            )

        argument_keys = set(
            arguments.keys()
        )

        missing_keys = (
            self.REQUIRED_ARGUMENTS
            - argument_keys
        )

        if missing_keys:

            raise ValueError(
                "Missing tool arguments: "
                f"{sorted(missing_keys)}"
            )

        allowed_keys = (
            self.REQUIRED_ARGUMENTS
            | self.OPTIONAL_ARGUMENTS
        )

        unexpected_keys = (
            argument_keys
            - allowed_keys
        )

        if unexpected_keys:

            raise ValueError(
                "Unexpected tool arguments: "
                f"{sorted(unexpected_keys)}"
            )

        return arguments

    def _build_request(
        self,
        arguments: dict,
    ) -> AnalysisRequest:

        return AnalysisRequest(
            ticker=arguments["ticker"].upper(),
            expiration=arguments["expiration"],
            analysis_types=arguments[
                "analysis_types"
            ],
            force_refresh=arguments.get(
                "force_refresh",
                False,
            ),
        )