from schemas.gex_result import GEXAnalysisResult
from analysis.gex_calculation import ContractGEX








class GEXAnalyzer:
    """
    Analyze ContractGEX list.

    Input:

        list[ContractGEX]


    Output:

        GEXAnalysisResult


    Responsibility:

        ContractGEX[]
              |
              ↓
        GEX Summary


    Does NOT:
        - calculate gamma
        - calculate single contract GEX
    """



    def analyze(
        self,
        gex_list: list[ContractGEX]
    ) -> GEXAnalysisResult:


        # ==========================
        # Exposure accumulator
        # ==========================

        total_gex = 0.0

        call_gex = 0.0

        put_gex = 0.0



        # ==========================
        # Top 3 buffers
        # ==========================

        call_top = []

        put_top = []



        # ==========================
        # Single pass
        # ==========================

        for item in gex_list:


            # total

            total_gex += item.gex



            # CALL

            if item.option_type == "CALL":

                call_gex += item.gex

                self.update_top3(
                    call_top,
                    item
                )



            # PUT

            elif item.option_type == "PUT":

                put_gex += item.gex

                self.update_top3(
                    put_top,
                    item
                )



        return GEXAnalysisResult(


            call_top_gex=
                self.get_rank(
                    call_top,
                    0
                ),

            call_2nd_top_gex=
                self.get_rank(
                    call_top,
                    1
                ),

            call_3rd_top_gex=
                self.get_rank(
                    call_top,
                    2
                ),



            put_top_gex=
                self.get_rank(
                    put_top,
                    0
                ),

            put_2nd_top_gex=
                self.get_rank(
                    put_top,
                    1
                ),

            put_3rd_top_gex=
                self.get_rank(
                    put_top,
                    2
                ),



            total_gex=total_gex,

            call_gex=call_gex,

            put_gex=put_gex

        )



    def update_top3(
        self,
        top_list: list[ContractGEX],
        item: ContractGEX
    ):
        """
        Maintain top 3 absolute GEX.

        Keep only three objects.
        """


        top_list.append(item)


        top_list.sort(
            key=lambda x: abs(x.gex),
            reverse=True
        )


        if len(top_list) > 3:

            top_list.pop()



    def get_rank(
        self,
        top_list: list[ContractGEX],
        index: int
    ) -> ContractGEX | None:
        """
        Get ranked item safely.
        """


        if len(top_list) <= index:

            return None


        return top_list[index]