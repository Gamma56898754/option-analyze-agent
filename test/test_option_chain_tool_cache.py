from cache.option_chain_cache import OptionChainCache
from schemas.expiration_info import ExpirationInfo
from tools.option_chain_tool import OptionChainTool


class FakeClient:

    def __init__(self):
        self.expiration_overview_calls = 0
        self.option_chain_calls = 0

    def get_expiration_overview(
        self,
        ticker: str,
    ) -> str:

        self.expiration_overview_calls += 1

        return "<fake expiration overview>"

    def get_option_chain(
        self,
        ticker: str,
        expiration: str,
        expiration_type: str,
    ) -> str:

        self.option_chain_calls += 1

        return "<fake option chain>"


class FakeRuntime:

    def __init__(self):
        self.client = FakeClient()
        self.option_chain_cache = OptionChainCache()


class FakeMarketTimeTool:

    def get_market_context(self):
        return object()


class FakeExpirationResolver:

    def resolve(
        self,
        html: str,
        market_context: object,
    ) -> list[ExpirationInfo]:

        return [
            ExpirationInfo(
                expiration_date="2026-08-17",
                expiration_type="w",
                dte=2,
            )
        ]


class FakeParser:

    def parse(
        self,
        chain_html: str,
        ticker: str,
        expiration_date: str,
    ) -> list:

        return []

    def parse_underlying_price(
        self,
        chain_html: str,
    ) -> float:

        return 100.0


def main():

    runtime = FakeRuntime()

    tool = OptionChainTool(
        runtime
    )

    tool.market_time_tool = FakeMarketTimeTool()
    tool.resolver = FakeExpirationResolver()
    tool.parser = FakeParser()

    first_result, first_quality_report = (
        tool.run_with_data_quality(
        ticker="TSLA",
        expiration_date="2026-08-17",
        )
    )

    assert first_quality_report.cache_state == "miss"
    assert first_quality_report.contract_count == 0
    assert first_quality_report.warnings

    assert (
        runtime.client.expiration_overview_calls
        == 1
    )

    assert (
        runtime.client.option_chain_calls
        == 1
    )

    second_result, second_quality_report = (
        tool.run_with_data_quality(
        ticker="TSLA",
        expiration_date="2026-08-17",
        )
    )

    assert second_result is first_result
    assert second_quality_report.cache_state == "hit"
    assert second_quality_report.fetched_at == (
        first_quality_report.fetched_at
    )

    assert (
        runtime.client.expiration_overview_calls
        == 1
    )

    assert (
        runtime.client.option_chain_calls
        == 1
    )

    refreshed_result, refreshed_quality_report = (
        tool.run_with_data_quality(
        ticker="TSLA",
        expiration_date="2026-08-17",
        force_refresh=True,
        )
    )

    assert refreshed_result is not first_result
    assert refreshed_quality_report.cache_state == "bypass"

    assert (
        runtime.client.expiration_overview_calls
        == 2
    )

    assert (
        runtime.client.option_chain_calls
        == 2
    )

    cached_after_refresh, cached_quality_report = (
        tool.run_with_data_quality(
        ticker="TSLA",
        expiration_date="2026-08-17",
        )
    )

    assert cached_after_refresh is refreshed_result
    assert cached_quality_report.cache_state == "hit"
    assert cached_quality_report.fetched_at == (
        refreshed_quality_report.fetched_at
    )

    assert (
        runtime.client.expiration_overview_calls
        == 2
    )

    assert (
        runtime.client.option_chain_calls
        == 2
    )

    print(
        "OptionChainTool cache "
        "and force-refresh test passed."
    )


if __name__ == "__main__":
    main()
