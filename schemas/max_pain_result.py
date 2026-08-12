from dataclasses import dataclass


@dataclass
class MaxPainResult:
    """
    Result of max pain calculation.

    Max pain represents the strike price
    where total option holder loss is minimized.
    """


    max_pain_price: float

    total_loss: float

    current_price: float

    distance_percent: float