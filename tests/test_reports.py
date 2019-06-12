import pytest
from typing import List
from reporting.reports import Report, PromotionReport


class TestReports:
    @pytest.mark.parametrize(
        "report_type, parameters, expected_output",
        [
            (PromotionReport, ['ethnicity', 'fls', '2019-09-01'],
             ['characteristic,number promoted,percentage promoted\r', 'White British,5,50%\r', 'Black British,7,70%\r','']),
            (PromotionReport, ['ethnicity', 'sls', '2019-09-01'],
             ['characteristic,number promoted,percentage promoted\r', 'White British,2,40%\r', 'Black British,3,60%\r','']),
        ]
    )
    def test_reports(self, report_type: Report, parameters: List[str], expected_output: str, test_session,
                     test_ethnicities, test_multiple_candidates_multiple_ethnicities):

        output = PromotionReport(*parameters).return_data(filename='test-ethnicity-promotion')
        assert output.data.decode("UTF-8").split('\n') == expected_output