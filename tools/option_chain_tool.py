from schemas.option_chain_result import OptionChainResult

from data.parser import OptionChainParser

from tools.expiration_resolver import ExpirationResolver
from tools.market_time_tool import MarketTimeTool

from core.exceptions import ExpirationNotFoundError
from schemas.data_quality_report import DataQualityReport
import time
from datetime import datetime, timezone

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

    DATA_SOURCE = "OptionCharts"

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

        result, _ = self.run_with_data_quality(
            ticker=ticker,
            expiration_date=expiration_date,
            force_refresh=force_refresh,
            trace_id=trace_id,
        )

        return result

    def run_with_data_quality(
        self,
        ticker: str,
        expiration_date: str,
        force_refresh: bool = False,
        trace_id: str | None = None,
    ) -> tuple[OptionChainResult, DataQualityReport]:
        """Return the chain and per-request provenance without mutating cache."""

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
            cached_entry = self.cache.get_entry(
                ticker=ticker,
                expiration=expiration_date,
            )

            if cached_entry is not None:
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

                return (
                    cached_entry.result,
                    self._build_data_quality_report(
                        fetched_at=cached_entry.cached_at,
                        cache_state="hit",
                        contract_count=len(
                            cached_entry.result.contracts
                        ),
                        underlying_price=(
                            cached_entry.result.underlying_price
                        ),
                    ),
                )

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

        fetched_at = datetime.now(timezone.utc)

        self.cache.set(
            ticker=ticker,
            expiration=expiration_date,
            result=option_chain_result,
            now=fetched_at,
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

        cache_state = (
            "bypass"
            if force_refresh
            else "miss"
        )

        return (
            option_chain_result,
            self._build_data_quality_report(
                fetched_at=fetched_at,
                cache_state=cache_state,
                contract_count=len(contracts),
                underlying_price=underlying_price,
            ),
        )

    def _build_data_quality_report(
        self,
        fetched_at: datetime,
        cache_state: str,
        contract_count: int,
        underlying_price: float,
    ) -> DataQualityReport:
        """Report only quality signals observable from the retrieved chain."""

        warnings = []

        if contract_count == 0:
            warnings.append(
                "The retrieved option chain contains no contracts."
            )

        if underlying_price <= 0:
            warnings.append(
                "The retrieved option chain has no valid underlying price."
            )

        return DataQualityReport(
            source=self.DATA_SOURCE,
            fetched_at=fetched_at,
            cache_state=cache_state,
            contract_count=contract_count,
            warnings=warnings,
        )
