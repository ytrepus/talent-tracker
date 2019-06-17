from datetime import date
from app.models import Ethnicity, Scheme
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

    @abstractmethod
    def generate_report_data(self):
        print("Not implemented yet!")

    def return_data(self):
        headers = Headers()
        headers["Content-Disposition"] = f"attachment; filename={self.filename}.csv"
        headers["Content-type"] = "text/csv"

        return Response(
            stream_with_context(self.generate_report_data()),
            mimetype='text/csv', headers=headers
        )


class PromotionReport(Report):
    def __init__(self, characteristic: str, scheme: str, year: str):
        super().__init__()
        self.characteristic = characteristic
        self.table = self.tables.get(self.characteristic)
        self.scheme = Scheme.query.filter_by(name=f'{scheme}').first()
        self.promoted_before_date = date(int(year) + 1, 3, 1)  # can't take credit for promotions within first 3 months
        self.headers = ['characteristic', 'number substantively promoted', 'percentage substantively promoted',
                        'number temporarily promoted', 'percentage temporarily promoted', 'total in group']
        self.filename = f"{characteristic}-{scheme}-{year}"

    def generate_report_data(self):
        """
        Search for promoted candidates and group them by characteristic. Provide an absolute number promoted
        and the percentage of that group promoted
        :return:
        :rtype:
        """
        def decimal_or_none(first_number, second_number):
            try:
                return first_number / second_number
            except ZeroDivisionError:
                return 0

        def promoted_candidates(characteristic, temporary):
            candidates = len([candidate for candidate in characteristic.candidates
                              if candidate.promoted(self.promoted_before_date, temporary=temporary)
                              and candidate.current_scheme() == self.scheme])  # noqa
            total_candidates = len(characteristic.candidates)
            return [candidates, decimal_or_none(candidates, total_candidates)]

        def line_writer(characteristic):
            line = [f"{characteristic.value}"]
            line.extend(promoted_candidates(characteristic, False))
            line.extend(promoted_candidates(characteristic, True))
            line.append(len(characteristic.candidates))
            return line

        output = []
        characteristics = self.table.query.all()
        for characteristic in characteristics:
            output.append(line_writer(characteristic))
        print(output)

        data = StringIO()
        w = csv.writer(data)

        # write header
        w.writerow(self.headers)
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        # write each item
        for item in output:
            w.writerow((
                item[0],
                item[1],
                "{0:.0%}".format(item[2]),  # format decimal as percentage
                item[3],
                "{0:.0%}".format(item[4]),  # format decimal as percentage
                item[5]
            )
            )
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
