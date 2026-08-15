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