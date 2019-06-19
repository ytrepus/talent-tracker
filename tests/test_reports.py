import pytest
from typing import List
from reporting.reports import Report, EthnicityPromotionReport
from app.models import Ethnicity, Candidate


class TestReports:
    @pytest.mark.parametrize(
        "parameters, white_british_promoted, black_british_promoted, scheme_id, expected_output",
        [
            (['FLS', 2019], .5, .7, 1,
             ['characteristic,number substantively promoted,percentage substantively promoted,'
              'number temporarily promoted,percentage temporarily promoted,total in group\r',
              'White British,5,50%,0,0%,10\r', 'Black British,7,70%,0,0%,10\r', '']),
            (['SLS', 2019], .4, .6, 2,
             ['characteristic,number substantively promoted,percentage substantively promoted,'
              'number temporarily promoted,percentage temporarily promoted,total in group\r',
              'White British,4,40%,0,0%,10\r', 'Black British,6,60%,0,0%,10\r', '']),
        ]
    )
    def test_reports(self, parameters: List[str], white_british_promoted, black_british_promoted,
                     scheme_id, expected_output: str, test_ethnicities, scheme_appender,
                     test_multiple_candidates_multiple_ethnicities, candidates_promoter):
        bb_candidates = Candidate.query.filter_by(
            ethnicity_id=Ethnicity.query.filter_by(value="Black British").first().id).all()
        wb_candidates = Candidate.query.filter_by(
            ethnicity_id=Ethnicity.query.filter_by(value="White British").first().id).all()
        candidates_promoter(bb_candidates, black_british_promoted)
        candidates_promoter(wb_candidates, white_british_promoted)
        scheme_appender(bb_candidates, scheme_id)
        scheme_appender(wb_candidates, scheme_id)
        output = EthnicityPromotionReport(*parameters).return_data()
        assert output.data.decode("UTF-8").split('\n') == expected_output

    @pytest.mark.parametrize("characteristic",
                             [
                                 ('gender')
                             ])
    def test_protected_characteristic_promotion_report(self,characteristic, test_genders, test_candidates):
        assert False
