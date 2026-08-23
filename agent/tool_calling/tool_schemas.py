OPTION_ANALYSIS_TOOL = {
    "type": "function",
    "function": {
        "name": "run_option_analysis",
        "description": (
            "Retrieve the option chain for a stock ticker and run one or more "
            "options analyses. Supported analyses are GEX, DEX, open interest, "
            "and max pain. Use this tool when the user requests new options data "
            "or asks to refresh existing data."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": (
                        "The uppercase stock ticker symbol, for example TSLA, "
                        "AAPL, or NVDA."
                    ),
                },
                "expiration": {
                    "type": "string",
                    "description": (
                        "The option expiration date in YYYY-MM-DD format."
                    ),
                },
                "analysis_types": {
                    "type": "array",
                    "description": (
                        "The requested analysis types. Use one or more values."
                    ),
                    "items": {
                        "type": "string",
                        "enum": [
                            "gex",
                            "dex",
                            "oi",
                            "maxpain",
                        ],
                    },
                    "minItems": 1,
                },
                "force_refresh": {
                    "type": "boolean",
                    "description": (
                        "Set true only when the user explicitly asks to refresh, "
                        "update, or ignore cached option-chain data."
                    ),
                },
            },
            "required": [
                "ticker",
                "expiration",
                "analysis_types",
            ],
            "additionalProperties": False,
        },
    },
}

OPTION_ANALYSIS_TOOLS = [
    OPTION_ANALYSIS_TOOL,
]