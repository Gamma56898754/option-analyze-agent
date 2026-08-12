from dataclasses import dataclass


@dataclass
class DEXResult:

    call_dex: float

    put_dex: float

    total_dex: float