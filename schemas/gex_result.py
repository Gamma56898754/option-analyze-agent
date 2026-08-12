from dataclasses import dataclass
from analysis.gex_calculation import ContractGEX

@dataclass
class GEXAnalysisResult:
    """
    Aggregated GEX analysis result.

    Contains:
    - Top 3 Call GEX contracts
    - Top 3 Put GEX contracts
    - Total exposure
    """

    # CALL端前三大GEX
    call_top_gex: ContractGEX | None

    call_2nd_top_gex: ContractGEX | None

    call_3rd_top_gex: ContractGEX | None


    # PUT端前三大GEX
    put_top_gex: ContractGEX | None

    put_2nd_top_gex: ContractGEX | None

    put_3rd_top_gex: ContractGEX | None


    # 汇总
    total_gex: float

    call_gex: float

    put_gex: float
