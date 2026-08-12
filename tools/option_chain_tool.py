from schemas.option_chain_result import OptionChainResult

from data.parser import OptionChainParser

from tools.expiration_resolver import ExpirationResolver
from tools.market_time_tool import MarketTimeTool


class OptionChainTool:
    """
    Option Chain Tool

    输入:
        ticker
        expiration_date

    输出:
        OptionChainResult

    依赖:
        runtime提供client

    """

    def __init__(self, runtime):

        # 长生命周期资源
        self.client = runtime.client


        # 无状态组件
        self.parser = OptionChainParser()

        self.resolver = ExpirationResolver()

        self.market_time_tool = MarketTimeTool()



    def run(
        self,
        ticker: str,
        expiration_date: str
    ) -> OptionChainResult:


        # ==========================
        # 1. 获取当前市场时间
        # ==========================

        market_context = (
            self.market_time_tool
            .get_market_context()
        )


        # ==========================
        # 2. 获取expiration overview
        # 判断 w / m
        # ==========================

        expiration_html = (
            self.client
            .get_expiration_overview(
                ticker
            )
        )


        expiration_infos = (
            self.resolver
            .resolve(
                expiration_html,
                market_context
            )
        )


        target_expiration = None


        for info in expiration_infos:

            if info.expiration_date == expiration_date:
                target_expiration = info
                break


        if target_expiration is None:

            raise ValueError(
                f"Expiration not found: {expiration_date}"
            )


        # ==========================
        # 3. 获取option chain
        # ==========================

        chain_html = (
            self.client
            .get_option_chain(
                ticker=ticker,
                expiration=expiration_date,
                expiration_type=(
                    target_expiration.expiration_type
                )
            )
        )


        # ==========================
        # 4. HTML解析
        # ==========================

        contracts = (
            self.parser
            .parse(
                chain_html,
                ticker,
                expiration_date
            )
        )


        # ==========================
        # 5. 获取现价
        # ==========================

        underlying_price = (
            self.parser
            .parse_underlying_price(
                chain_html
            )
        )


        # ==========================
        # 6. 返回统一数据结构
        # ==========================

        return OptionChainResult(

            ticker=ticker,

            expiration_info=target_expiration,

            underlying_price=underlying_price,

            contracts=contracts
        )