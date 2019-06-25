from datetime import date
from typing import List, Union, Tuple
from sqlalchemy import and_

from app.models import Ethnicity, Scheme, Gender, Candidate, Application, Sexuality, WorkingPattern, Belief, AgeRange
from abc import ABC, abstractmethod
from io import StringIO
from werkzeug.datastructures import Headers
from flask import Response, stream_with_context
import csv


class Report(ABC):
    def __init__(self):
        self.tables = {
            'ethnicity': Ethnicity
        }
        self.filename = None
        self.headers = []
        self.filename = ''

    @abstractmethod
    def write_row(self, row_data, data_object, csv_writer):
        raise NotImplementedError

    def write_headers(self, data_object, csv_writer):
        csv_writer.writerow(self.headers)
        return data_object.getvalue()

    @staticmethod
    def decimal_or_none(first_number, second_number):
        try:
            return first_number / second_number
        except ZeroDivisionError:
            return 0

    @abstractmethod
    def get_data(self):
        raise NotImplementedError

    def generate_report_data(self):
        output = self.get_data()
        data = StringIO()
        w = csv.writer(data)

        # write header
        yield self.write_headers(data, w)
        data.seek(0)
        data.truncate(0)

        # write each item
        for item in output:
            yield self.write_row(item, data, w)
            data.seek(0)
            data.truncate(0)

    def return_data(self):
        headers = Headers()
        headers["Content-Disposition"] = f"attachment; filename={self.filename}.csv"
        headers["Content-type"] = "text/csv"

        return Response(
            stream_with_context(self.generate_report_data()),
            mimetype='text/csv', headers=headers
        )


class PromotionReport(Report, ABC):
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
        pass

    def row_writer(self, characteristic) -> List:
        pass

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


class CharacteristicPromotionReport(PromotionReport):
    def __init__(self, scheme: str, year: str, attribute: str):
        super().__init__(scheme, year, attribute)
        self.tables = {'ethnicity': Ethnicity, 'gender': Gender, 'sexuality': Sexuality, 'belief': Belief,
                       'working_pattern': WorkingPattern, 'age_range': AgeRange}
        self.table = self.tables.get(self.attribute)

    def promoted_candidates_with_this_characteristic(self, characteristic, temporary):
        """
        Takes a row from one of the ProtectedCharacteristic tables (Ethnicity, WorkingPattern, etc) and returns the
        number of candidates with that characteristic who have also been promoted in the timeframe allowed by the class
        :param characteristic:
        :type characteristic:
        :param temporary:
        :type temporary:
        :return:
        :rtype:
        """

        eligible_candidates = [candidate for candidate in self.eligible_candidates()
                               if getattr(candidate, self.attribute) == characteristic]
        promoted_candidates = [candidate for candidate in eligible_candidates
                               if candidate.promoted(self.promoted_before_date, temporary=temporary)]
        total_candidates = len(eligible_candidates)
        return [len(promoted_candidates), self.decimal_or_none(len(promoted_candidates), total_candidates)]

    def row_writer(self, characteristic):
        line = [f"{characteristic.value}"]
        line.extend(self.promoted_candidates_with_this_characteristic(characteristic, False))
        line.extend(self.promoted_candidates_with_this_characteristic(characteristic, True))
        line.append(len([candidate for candidate in self.eligible_candidates()
                         if getattr(candidate, self.attribute) == characteristic]))
        return line

    def get_data(self):
        output = []
        characteristics = self.table.query.all()
        for characteristic in characteristics:
            output.append(self.row_writer(characteristic))
        return output


class BooleanCharacteristicPromotionReport(PromotionReport):
    def __init__(self, scheme: str, year: str, attribute: str):
        super().__init__(scheme, year, attribute)
        self.human_readable_characteristics = {
            'long_term_health_condition': {
                True: "People with a disability", False: "People without a disability", None: "No answer provided"
            },
            'caring_responsibility': {
                True: "I have caring responsibilities", False: "I do not have caring responsibilities",
                None: "No answer provided"
            }
        }
        self.human_readable_row_titles = self.human_readable_characteristics.get(self.attribute)

    def get_data(self):
        characteristics = [True, False, None]
        return [self.row_writer(characteristic) for characteristic in characteristics]

    def row_writer(self, characteristic: bool):
        line = [f"{self.human_readable_row_titles.get(characteristic)}"]
        line.extend(self.promoted_candidates_with_this_characteristic(characteristic, temporary=False))
        line.extend(self.promoted_candidates_with_this_characteristic(characteristic, temporary=True))
        line.append(len(Candidate.query.filter(getattr(Candidate, self.attribute).is_(characteristic)).all()))
        return line

    def promoted_candidates_with_this_characteristic(self, characteristic: bool, temporary: bool):
        eligible_candidates = [candidate for candidate in self.eligible_candidates()
                               if getattr(candidate, self.attribute) == characteristic]
        promoted_candidates = [candidate for candidate in eligible_candidates
                               if candidate.promoted(self.promoted_before_date, temporary=temporary)]
        total_candidates = len(eligible_candidates)
        return [len(promoted_candidates), self.decimal_or_none(len(promoted_candidates), total_candidates)]


class OfferPromotionReport(PromotionReport):
    def __init__(self, scheme, year, attribute):
        super().__init__(scheme, year, attribute)
        self.upper_attribute = attribute.upper()
        self.human_readable_row_titles = {
            True: f"Candidates eligible for {self.upper_attribute}",
            False: f"Candidates who took up {self.upper_attribute} offer"
        }

    def promoted_candidates_with_this_characteristic(self, characteristic: bool, temporary: bool) -> Tuple[int, float]:
        """
        The two outputs here are: the number of candidates promoted who are on meta/delta, and the number of
        candidates promoted who were eligible for meta/delta
        :param characteristic:
        :type characteristic:
        :param temporary:
        :type temporary:
        :return:
        :rtype:
        """
        eligible_candidates = [candidate for candidate in self.eligible_candidates()
                               if getattr(candidate.applications[0], self.attribute) == characteristic]
        promoted_candidates = [candidate for candidate in eligible_candidates
                               if candidate.promoted(self.promoted_before_date, temporary=temporary)]
        total_candidates = len(eligible_candidates)
        return len(promoted_candidates), self.decimal_or_none(len(promoted_candidates), total_candidates)

    def row_writer(self, characteristic: bool) -> List[Union[str, int, float]]:
        line = [f"{self.human_readable_row_titles.get(characteristic)}"]
        line.extend(self.promoted_candidates_with_this_characteristic(characteristic, temporary=False))
        line.extend(self.promoted_candidates_with_this_characteristic(characteristic, temporary=True))
        return line


class MetaOfferPromotionReport(OfferPromotionReport):
    def __init__(self, scheme, year, attribute):
        super().__init__(scheme, year, attribute)

    def eligible_candidates(self) -> List[Candidate]:
        return [candidate for candidate in super().eligible_candidates if candidate.ethnicity.bame]


class DisabilityReport(PromotionReport):
    def candidates_with_a_disability(self):
        return [candidate for candidate in super().eligible_candidates() if candidate.long_term_health_condition]

    def candidates_on_delta(self):
        return [candidate for candidate in super().eligible_candidates() if candidate.applications[0].delta]


class DeltaOfferPromotionReport(OfferPromotionReport, DisabilityReport):
    def __init__(self, scheme, year, attribute):
        super().__init__(scheme, year, attribute)

    def eligible_candidates(self):
        return self.candidates_with_a_disability()

    def get_data(self):
        """
        This method generates only two rows of data. The first is people with a disability who've been promoted.
        The second is people with a disability on DELTA who've been promoted
        :return:
        :rtype:
        """
        output = []
        row_metadata = [
            ("Candidates eligible for DELTA", self.candidates_with_a_disability),
            ("Candidates on DELTA", self.candidates_on_delta)
        ]
        for tupl in row_metadata:
            output.append(self.row_writer(tupl[0], tupl[1]))
        return output

    def row_writer(self, row_header: str, candidate_list_generator: callable):
        output = [row_header]
        total_candidates = candidate_list_generator()
        output.extend(self.chunk_writer(False, total_candidates))
        output.extend(self.chunk_writer(True, total_candidates))
        output.append(len(total_candidates))
        return output

    def chunk_writer(self, temporary, candidates):
        promoted_number = len(self.promoted_candidates(temporary, candidates))
        return [promoted_number, self.decimal_or_none(promoted_number, len(candidates))]
