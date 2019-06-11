import pytest
from typing import List
from reporting.reports import Report, PromotionReport


class TestReports:
    @pytest.mark.parametrize(
        "report_type, parameters, expected_output",
        [
            (PromotionReport, ['ethnicity', 'fls'],
             ['characteristic,percentage promoted,number promoted\r', 'white,50%,90\r', 'bame,33%,5\r', '']),
            (PromotionReport, ['ethnicity', 'sls'],
             ['characteristic,percentage promoted,number promoted\r', 'white,70%,90\r', 'bame,33%,5\r', ''])
        ]
    )
    def test_reports(self, report_type: Report, parameters: List[str], expected_output: str, test_database):
        output = PromotionReport(*parameters).return_data(filename='test-ethnicity-promotion')
        assert output.data.decode("UTF-8").split('\n') == expected_output
