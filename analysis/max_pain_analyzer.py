from dataclasses import dataclass

from schemas.option_contract import OptionContract
from schemas.max_pain_result import MaxPainResult



class MaxPainAnalyzer:
    """
    Calculate option max pain.

    Optimized algorithm:

    1. Separate CALL and PUT
    2. Sort strikes
    3. Build cumulative OI and OI*Strike
    4. Calculate pain in O(logN)

    Complexity:
        O(N log N)
    """



    def analyze(
        self,
        contracts: list[OptionContract],
        current_price: float
    ) -> MaxPainResult:


        calls = []
        puts = []


        # -----------------------
        # Separate option types
        # -----------------------

        for contract in contracts:

            if contract.option_type == "CALL":

                calls.append(
                    (
                        contract.strike,
                        contract.open_interest
                    )
                )


            elif contract.option_type == "PUT":

                puts.append(
                    (
                        contract.strike,
                        contract.open_interest
                    )
                )



        # -----------------------
        # Sort strikes
        # -----------------------

        calls.sort(
            key=lambda x:x[0]
        )

        puts.sort(
            key=lambda x:x[0]
        )



        # -----------------------
        # Prepare prefix sums
        # -----------------------

        call_data = self.build_prefix(
            calls
        )


        put_data = self.build_prefix(
            puts
        )



        # Candidate prices
        # Usually all strikes

        strikes = sorted(
            set(
                [
                    strike
                    for strike, _ in calls + puts
                ]
            )
        )


        min_loss = float(
            "inf"
        )

        max_pain = None



        # -----------------------
        # Calculate pain
        # -----------------------

        for price in strikes:


            call_loss = self.calculate_call_loss(
                price,
                call_data
            )


            put_loss = self.calculate_put_loss(
                price,
                put_data
            )


            total_loss = (
                call_loss
                +
                put_loss
            )



            if total_loss < min_loss:

                min_loss = total_loss

                max_pain = price



        distance = (
            (
                max_pain
                -
                current_price
            )
            /
            current_price
        ) * 100



        return MaxPainResult(

            max_pain_price=max_pain,

            total_loss=min_loss,

            current_price=current_price,

            distance_percent=distance

        )



    def build_prefix(
        self,
        data: list[tuple]
    ):
        """
        Build cumulative data.

        Returns:

        {
            strikes,
            cumulative_OI,
            cumulative_OI_strike
        }

        """


        strikes = []

        oi_prefix = [0]

        oi_strike_prefix = [0]


        total_oi = 0

        total_oi_strike = 0



        for strike, oi in data:


            strikes.append(
                strike
            )


            total_oi += oi

            total_oi_strike += (
                strike * oi
            )


            oi_prefix.append(
                total_oi
            )


            oi_strike_prefix.append(
                total_oi_strike
            )



        return {

            "strikes": strikes,

            "oi": oi_prefix,

            "oi_strike": oi_strike_prefix

        }



    def calculate_call_loss(
        self,
        price,
        data
    ):

        """
        Call loss:

        SUM((price-strike)*OI)

        Only strikes below price.
        """


        import bisect


        strikes = data["strikes"]


        index = bisect.bisect_left(
            strikes,
            price
        )


        total_oi = data["oi"][index]

        total_oi_strike = (
            data["oi_strike"][index]
        )


        return (
            price * total_oi
            -
            total_oi_strike
        )



    def calculate_put_loss(
        self,
        price,
        data
    ):

        """
        Put loss:

        SUM((strike-price)*OI)

        Only strikes above price.
        """


        import bisect


        strikes = data["strikes"]


        index = bisect.bisect_right(
            strikes,
            price
        )


        total_oi = (
            data["oi"][-1]
            -
            data["oi"][index]
        )


        total_oi_strike = (
            data["oi_strike"][-1]
            -
            data["oi_strike"][index]
        )


        return (
            total_oi_strike
            -
            price * total_oi
        )