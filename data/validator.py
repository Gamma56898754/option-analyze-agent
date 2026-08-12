class OptionValidator:


    def validate(self, contract):

        warnings = []


        if (
            contract.bid is not None
            and contract.ask is not None
            and contract.bid > contract.ask
        ):
            warnings.append(
                "Bid greater than Ask"
            )


        if (
            contract.implied_volatility
            and contract.implied_volatility > 5
        ):
            warnings.append(
                "Extreme IV"
            )


        return warnings