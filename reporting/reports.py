from datetime import date
from typing import List
from sqlalchemy import and_

from app.models import Ethnicity, Scheme, Gender, Candidate, Application
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

    def eligible_candidates(self) -> List[Candidate]:
        """
        Candidates eligible to be reported on have an application whose scheme start date is aligned with ```year``` and
        whose Application -> Scheme -> name is the same as ```scheme```. For example, the 2019 FLS intake all have a
        scheme_start_date on their applications of 2019/03/01 and a scheme_id that references the 'FLS' scheme.
        :return:
        :rtype:
        """
        print(Application.query.filter(Application.scheme_start_date == self.intake_date,).all())
        eligible_applications = Application.query.filter(and_(
            Application.scheme_start_date == self.intake_date,
            Application.scheme_id == self.scheme.id
        )).all()
        return [application.candidate for application in eligible_applications]

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
    def __init__(self, scheme: str, year: str, table_name: str):
        super().__init__(scheme, year)
        self.table_name = table_name
        self.tables = {'ethnicity': Ethnicity, 'gender': Gender}
        self.table = self.tables.get(table_name)
        self.filename = f"promotions-by-{table_name}-{scheme}-{year}-generated-{date.today().strftime('5%d-%m-%Y')}"

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

    def line_writer(self, characteristic):
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
            output.append(self.line_writer(characteristic))
        return output


class BooleanCharacteristicPromotionReport(CharacteristicPromotionReport):
    def __init__(self, scheme: str, year: str, attribute: str):
        super().__init__(scheme, year, attribute)
        self.human_readable_characteristics = {
            'long_term_health_condition': {
                True: "People with a disability", False: "People without a disability", None: "No answer provided"
            },
            'caring_responsibilities': {
                True: "I have caring responsibilities", False: "I do not have caring responsibilities",
                None: "No answer provided"
            }
        }
        self.human_readable_row_titles = self.human_readable_characteristics.get(self.attribute)

    def get_data(self):
        characteristics = [True, False, None]
        return [self.line_writer(characteristic) for characteristic in characteristics]

    def line_writer(self, characteristic: bool):
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
