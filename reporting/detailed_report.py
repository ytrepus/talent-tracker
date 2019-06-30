from reporting.base_report import Report
from typing import List
from app.models import Candidate, Application
from sqlalchemy import and_
from datetime import datetime


class DetailedReport(Report):
    def __init__(self, cohorts: List[str], promoted, scheme):
        super().__init__(scheme)
        self.cohorts = cohorts
        self.promoted = promoted
        self.headers = [
            "candidate name", "candidate email", "cohort"
        ]

    def write_row(self, row_data, data_object, csv_writer):
        pass

    def get_data(self):
        if self.promoted:
            return self.get_promoted_candidates()
        else:
            return self.get_unpromoted_candidates()

    def eligible_candidates(self) -> List[Candidate]:
        """
        Eligible candidates are those on `intake` and are on `scheme`
        `intakes`
        :return: List[Candidate]
        """
        return [application.candidate for application in Application.query.filter(
            and_(
                Application.cohort in self.cohorts,
                Application.scheme_id == self.scheme.id
            )
        )]

    def get_promoted_candidates(self):
        return [candidate for candidate in self.eligible_candidates()
                if candidate.promoted(datetime.today(), temporary=True)
                or candidate.promoted(datetime.today(), temporary=False)]

    def get_unpromoted_candidates(self):
        return list(set(self.eligible_candidates()) - set(self.get_promoted_candidates()))
