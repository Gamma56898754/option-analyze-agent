class ExpirationNotFoundError(ValueError):
    """
    Requested expiration does not exist in
    the data source's available expiration list.
    """

    def __init__(
        self,
        ticker: str,
        requested_expiration: str,
        available_expirations: list[str],
    ):
        self.ticker = ticker
        self.requested_expiration = (
            requested_expiration
        )
        self.available_expirations = (
            available_expirations
        )

        super().__init__(
            f"Expiration not found: "
            f"{requested_expiration}"
        )

class MarketDataUnavailableError(RuntimeError):
    """
    The external market-data source could not
    complete a request for this user turn.
    """

    def __init__(
        self,
        source: str,
        operation: str,
        status_code: int | None = None,
    ):
        self.source = source
        self.operation = operation
        self.status_code = status_code

        detail = (
            f"{source} unavailable during {operation}"
        )

        if status_code is not None:
            detail += f" (HTTP {status_code})"

        super().__init__(detail)