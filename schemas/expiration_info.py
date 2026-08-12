from dataclasses import dataclass


@dataclass
class ExpirationInfo:

    expiration_date: str

    expiration_type: str

    dte: int