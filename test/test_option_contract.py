from data.option_contract import OptionContract


contract = OptionContract(

    ticker="TSLA",

    contract_symbol=
    "TSLA260810C00330000",

    expiration=
    "2026-08-10",

    option_type="CALL",

    strike=330,

    last=2.81,

    bid=2.80,

    mid=2.84,

    ask=2.88,

    volume=54174,

    open_interest=3441,

    implied_volatility=0.2922,

    delta=0.44,

    gamma=0.0454,

    theta=-0.59,

    vega=0.12

)


print(contract)