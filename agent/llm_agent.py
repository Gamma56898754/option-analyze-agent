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
        user_input: str
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
    ]
}

Rules:

1. ticker must be stock symbol.
2. expiration must be YYYY-MM-DD.
3. analysis_types only contains:
   gex
   dex
   oi
   maxpain

Return JSON only.

"""


        response = self.client.chat.completions.create(

            model="deepseek-v4-flash",

            messages=[

                {
                    "role":"system",
                    "content":system_prompt
                },

                {
                    "role":"user",
                    "content":user_input
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

            analysis_types=data["analysis_types"]

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