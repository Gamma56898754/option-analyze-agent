from dataclasses import dataclass

from schemas.option_contract import OptionContract
from schemas.expiration_info import ExpirationInfo


@dataclass
class OptionChainResult:

    ticker: str

    expiration_info: ExpirationInfo

    underlying_price: float

    contracts: list[OptionContract]