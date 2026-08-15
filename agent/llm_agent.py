from openai import OpenAI
import json 
import os

from dotenv import load_dotenv

load_dotenv()

from schemas.analysis_request import AnalysisRequest
from core.analysis_runner import AnalysisRunner
from core.request_validator import RequestValidator

from agent.result_formatter import ResultFormatter



class LLMAgent:


    def __init__(
        self,
        runtime,
        api_key,
        base_url="https://api.deepseek.com"
    ):


        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )


        self.runner = AnalysisRunner(
            runtime
        )


        self.validator = RequestValidator()


        self.formatter = ResultFormatter()



    def create_request(
        self,
        user_input: str,
        conversation_history: list[dict[str, str]] | None = None,
        last_successful_request: dict[str, object] | None = None,
        running_summary: str | None = None,
        market_date: str | None = None,
    ) -> AnalysisRequest:
        """
        Convert user language into AnalysisRequest.
        """


        system_prompt = """

You are an options analysis assistant.

Convert user requests into JSON.

Required format:

{
    "ticker": "TSLA",
    "expiration": "YYYY-MM-DD",
    "analysis_types": [
        "gex",
        "dex",
        "oi",
        "maxpain"
    ],
    "execution_mode": "run_analysis",
    "force_refresh": false
}

Rules:

1. ticker must be stock symbol.
2. expiration must be YYYY-MM-DD.
3. analysis_types only contains:
   gex
   dex
   oi
   maxpain
4. execution_mode only contains:
   run_analysis
   explain_existing
5. Use run_analysis when the user:
   - requests a new indicator
   - changes ticker or expiration
   - asks to refresh, update, or analyze current data
   - asks an ambiguous question
6. Use explain_existing only when the user clearly asks
   to explain, summarize, or elaborate on the immediately
   previous successful analysis result without requesting
   new data or a new indicator.
7. When uncertain, use run_analysis.
8. force_refresh must be true only when the user explicitly asks to:
   - refresh data
   - fetch the latest data
   - re-fetch the option chain
   - ignore cached data
9. force_refresh must be false for normal analysis requests
   and explain_existing requests.
10. When uncertain, use force_refresh = false.
11. Use the current US market date provided in the user message
    to interpret relative date expressions.
12. Do not invent a date when the user does not provide
    a date or a supported relative date expression.

Return JSON only.

"""
        history = conversation_history or []

        current_market_date = (
            market_date
            or "Not provided"
        )

        summary = running_summary or "None"

        previous_request = (
            json.dumps(
                last_successful_request,
                ensure_ascii=False
            )
            if last_successful_request
            else "None"
        )

        response = self.client.chat.completions.create(

            model="deepseek-v4-flash",

            messages=[

                {
                    "role": "system",
                    "content": system_prompt
                },

                *history,

                {
                    "role": "user",
                    "content": f"""
Current user request:

{user_input}

Current US market date in New York:

{current_market_date}

If the user uses a relative date expression,
interpret it relative to this market date.
Return expiration only in YYYY-MM-DD format.

Previous successful structured request:

Previous successful structured request:

{previous_request}

Conversation summary of earlier turns:

{summary}

Use previous conversation and the previous successful request
only to resolve references such as "same ticker" or "same date".

Return JSON only.
"""
                }
            ]

        )


        content = (
            response
            .choices[0]
            .message
            .content
        )


        data = json.loads(
            content
        )


        return AnalysisRequest(

            ticker=data["ticker"],

            expiration=data["expiration"],

            analysis_types=data["analysis_types"],

            execution_mode=data.get(
                "execution_mode",
                "run_analysis"
            ),

            force_refresh=data.get(
                "force_refresh",
                False
            )

        )


    def summarize_conversation(
        self,
        previous_summary: str | None,
        messages_to_summarize: list[dict[str, str]],
    ) -> str:
        """
        Compress earlier conversation turns into durable short-term context.
        """

        system_prompt = """
You summarize an options-analysis conversation for future turns.

Keep only information useful for correctly understanding a later user request:

- user intent and follow-up context
- resolved ticker, expiration, and requested analysis types
- stable user preferences or constraints explicitly stated by the user
- unresolved questions

Rules:

- Do not invent facts.
- Do not preserve detailed live market numbers as durable facts.
- Do not give trading advice.
- Merge the previous summary with the older conversation messages.
- Write a concise summary in the same language as the conversation.
- Do not retain conclusions about live option-market conditions
  as durable memory. They may become stale quickly.
- Do not infer a stable user preference from a single request.
  Only retain preferences explicitly stated by the user or repeated
  across the conversation.
"""

        response = self.client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": f"""
Previous summary:

{previous_summary or "None"}

Older conversation messages to summarize:

{json.dumps(messages_to_summarize, ensure_ascii=False, indent=2)}
""",
                },
            ],
        )

        return (
            response
            .choices[0]
            .message
            .content
        )


    def run(
        self,
        user_input:str
    ) -> str:


        # 1. LLM理解用户需求

        request = self.create_request(
            user_input
        )


        # 2. 验证

        self.validator.validate(
            request
        )


        # 3. 执行分析

        result = self.runner.run(
            request
        )


        # 4. 格式化输出

        analysis_context = self.formatter.format(
            result
        )

        answer = self.generate_analysis(
            user_input=user_input,
            analysis_context=analysis_context
        )

        return answer

    def generate_analysis(
        self,
        user_input: str,
        analysis_context: str
    ) -> str:
        """
        Let LLM analyze the calculated results.

        Input:
            user request
            formatted analysis result

        Output:
            final natural language answer
        """


        system_prompt = """

        You are an options analysis assistant.

        You will receive:

        1. User request
        2. Calculated option analysis results

        Your task:

        - Explain the important market information.
        - Analyze GEX, DEX, OI and Max Pain relationships.
        - Explain possible support/resistance levels.
        - Mention uncertainty and risk.
        - Do not invent any numbers.
        - Only use the provided analysis data.
        - The market data was retrieved from OptionCharts and
        calculated by this application, not provided by the user.
        - Never say that the user provided the market data.
        - When describing the data source, say it is based on this
        analysis's option-chain data snapshot retrieved by the agent.
        - Do not describe the data as real-time or latest unless the
        provided analysis data explicitly includes a retrieval timestamp.


        Answer in a professional but understandable way.

        """


        response = self.client.chat.completions.create(

            model="deepseek-v4-flash",

            messages=[

                {
                    "role": "system",
                    "content": system_prompt
                },

                {
                    "role": "user",
                    "content": f"""
                    User request:

                    {user_input}


                    Analysis result:

                    {analysis_context}


                    Please provide your analysis.
                    """
                                    }

                                ]

                            )


        return (
            response
            .choices[0]
            .message
            .content
        )