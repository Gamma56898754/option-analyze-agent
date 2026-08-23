import requests

from core.exceptions import (
    MarketDataUnavailableError,
)
from data.optionchart_client import (
    OptionChartClient,
)


class ConnectionFailingSession:

    def get(self, *args, **kwargs):
        raise requests.ConnectionError(
            "Simulated network failure"
        )


class StatusFailingResponse:

    status_code = 405
    text = ""


class StatusFailingSession:

    def get(self, *args, **kwargs):
        return StatusFailingResponse()


def test_network_error_becomes_domain_error():

    client = OptionChartClient(cookies=[])

    client.session = ConnectionFailingSession()

    try:

        client.get_expiration_overview(
            ticker="TSLA"
        )

    except MarketDataUnavailableError as exc:

        assert exc.source == "OptionCharts"

        assert exc.operation == (
            "expiration_overview"
        )

        assert exc.status_code is None

    else:

        raise AssertionError(
            "Expected MarketDataUnavailableError"
        )


def test_http_error_becomes_domain_error():

    client = OptionChartClient(cookies=[])

    client.session = StatusFailingSession()

    try:

        client.get_expiration_overview(
            ticker="TSLA"
        )

    except MarketDataUnavailableError as exc:

        assert exc.status_code == 405

    else:

        raise AssertionError(
            "Expected MarketDataUnavailableError"
        )


if __name__ == "__main__":

    test_network_error_becomes_domain_error()

    test_http_error_becomes_domain_error()

    print(
        "OptionCharts client error handling "
        "test passed."
    )