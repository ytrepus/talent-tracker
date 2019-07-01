from abc import ABC
from datetime import date
from typing import List

from sqlalchemy import and_

from app.models import Scheme, Candidate, Application
from reporting import Report


class PromotionReport(Report, ABC):
    """
    This class deals with reports that produce data about promotions. All promotions reports deal with an attribute -
    that might be a protected characteristic or a grouping like META or DELTA. All promotion reports have the same
    column headers and deal with a single intake year.
    """
    def __init__(self, scheme: str, year: str, attribute: str = None):
        super().__init__()
        self.attribute = attribute
        self.intake_date = date(int(year), 3, 1)  # assuming it starts in March every year
        self.scheme = Scheme.query.filter_by(name=f'{scheme}').first()
        self.promoted_before_date = date(int(year) + 1, 3, 1)  # can't take credit for promotions within first 3 months
        self.headers = ['characteristic', 'number substantively promoted', 'percentage substantively promoted',
                        'number temporarily promoted', 'percentage temporarily promoted', 'total in group']
        self.filename = f"promotions-by-{attribute}-{scheme}-{year}-generated-{date.today().strftime('5%d-%m-%Y')}"

    def get_data(self):
        output = []
        for tupl in self.get_row_metadata():
            output.append(self.row_writer(tupl[0], tupl[1]))
        return output

    def get_row_metadata(self):
        return NotImplementedError

    def row_writer(self, row_header, candidate_list):
        output = [row_header]
        output.extend(self.chunk_writer(False, candidate_list))
        output.extend(self.chunk_writer(True, candidate_list))
        output.append(len(candidate_list))
        return output

    def chunk_writer(self, temporary, candidates):
        promoted_number = len(self.promoted_candidates(temporary, candidates))
        return [promoted_number, self.decimal_or_none(promoted_number, len(candidates))]

    def eligible_candidates(self) -> List[Candidate]:
        """
        Candidates eligible to be reported on have an application whose scheme start date is aligned with ```year``` and
        whose Application -> Scheme -> name is the same as ```scheme```. For example, the 2019 FLS intake all have a
        scheme_start_date on their applications of 2019/03/01 and a scheme_id that references the 'FLS' scheme.
        :return:
        :rtype:
        """
        eligible_applications = Application.query.filter(and_(
            Application.scheme_start_date == self.intake_date,
            Application.scheme_id == self.scheme.id
        )).all()
        return [application.candidate for application in eligible_applications]

    def promoted_candidates(self, temporary, candidates: List[Candidate]):
        return [candidate for candidate in candidates if candidate.promoted(self.promoted_before_date, temporary)]

    def write_row(self, row_data, data_object, csv_writer):
        """
        Format the row data in a human-readable form and write it out
        """
        csv_writer.writerow((
            row_data[0],
            row_data[1],
            "{0:.0%}".format(row_data[2]),  # format decimal as percentage
            row_data[3],
            "{0:.0%}".format(row_data[4]),  # format decimal as percentage
            row_data[5]
        )
        )
        return data_object.getvalue()