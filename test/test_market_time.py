from tools.market_time_tool import MarketTimeTool



def main():

    tool = MarketTimeTool()


    context = tool.get_market_context()


    print(
        "Current Time:",
        context.current_time
    )


    print(
        "Timezone:",
        context.timezone
    )


    print(
        "Market Status:",
        context.market_status
    )



if __name__ == "__main__":

    main()