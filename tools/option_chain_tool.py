from schemas.option_chain_result import OptionChainResult

from data.parser import OptionChainParser

from tools.expiration_resolver import ExpirationResolver
from tools.market_time_tool import MarketTimeTool

from core.exceptions import ExpirationNotFoundError
import time

from core.trace import log_trace_event


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

        self.cache = runtime.option_chain_cache

        # 无状态组件
        self.parser = OptionChainParser()

        self.resolver = ExpirationResolver()

        self.market_time_tool = MarketTimeTool()

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
        ticker: str,
        expiration_date: str,
        force_refresh: bool = False,
        trace_id: str | None = None,
    ) -> OptionChainResult:

        started_at = time.perf_counter()

        # ==========================
        # 0.强制刷新或读取缓存
        # ==========================
        if force_refresh:
            print(
            "OptionChain cache bypass: force refresh",
            ticker,
            expiration_date,
        )
            self._trace(
                trace_id,
                "option_chain_cache_bypassed",
                ticker=ticker,
                expiration=expiration_date,
            )
        else:
            cached_result = self.cache.get(
                ticker=ticker,
                expiration=expiration_date,
            )

            if cached_result is not None:
                print(
                    "OptionChain cache hit:",
                    ticker,
                    expiration_date,
                )

                self._trace(
                    trace_id,
                    "option_chain_cache_hit",
                    ticker=ticker,
                    expiration=expiration_date,
                    duration_ms=round(
                        (time.perf_counter() - started_at) * 1000,
                        2,
                    ),
                )

                return cached_result

            print(
                "OptionChain cache miss:",
                ticker,
                expiration_date,
            )

            self._trace(
                trace_id,
                "option_chain_cache_miss",
                ticker=ticker,
                expiration=expiration_date,
            )

        self._trace(
            trace_id,
            "option_chain_fetch_started",
            ticker=ticker,
            expiration=expiration_date,
        )

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

            available_expirations = sorted(
                info.expiration_date
                for info in expiration_infos
            )

            raise ExpirationNotFoundError(
                ticker=ticker,
                requested_expiration=expiration_date,
                available_expirations=(
                    available_expirations
                ),
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

        option_chain_result = OptionChainResult(

            ticker=ticker,

            expiration_info=target_expiration,

            underlying_price=underlying_price,

            contracts=contracts
        )

        self.cache.set(
            ticker=ticker,
            expiration=expiration_date,
            result=option_chain_result,
        )

        self._trace(
            trace_id,
            "option_chain_fetch_completed",
            ticker=ticker,
            expiration=expiration_date,
            contract_count=len(contracts),
            duration_ms=round(
                (time.perf_counter() - started_at) * 1000,
                2,
            ),
        )

        return option_chain_result
