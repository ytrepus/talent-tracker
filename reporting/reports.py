from app.models import Ethnicity, Scheme, Candidate
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
        super(Report, self).__init__()

    @abstractmethod
    def generate_report_data(self):
        print("Not implemented yet!")

    def return_data(self, filename: str):
        headers = Headers()
        headers["Content-Disposition"] = f"attachment; filename={filename}.csv"
        headers["Content-type"] = "text/csv"

        return Response(
            stream_with_context(self.generate_report_data()),
            mimetype='text/csv', headers=headers
        )


class PromotionReport(Report):
    def __init__(self, characteristic: str, scheme: str, cutoff_date: str):
        super().__init__()
        self.characteristic = characteristic
        self.table = self.tables.get(self.characteristic)
        self.scheme = Scheme.query.filter_by(name=f'{scheme}').first()
        self.promoted_before_date = cutoff_date
        self.headers = ['characteristic', 'number promoted', 'percentage promoted']

    def generate_report_data(self):
        """
        Search for promoted candidates and group them by characteristic. Provide an absolute number promoted
        and the percentage of that group promoted
        :return:
        :rtype:
        """
        output = []
        characteristics = self.table.query.all()
        for characteristic in characteristics:
            print([candidate for candidate in characteristic.candidates
                                       if candidate.promoted(self.promoted_before_date)
                                       and candidate.current_scheme() == self.scheme
                                       ])
            promoted_candidates = len([candidate for candidate in characteristic.candidates
                                       if candidate.promoted(self.promoted_before_date)
                                       and candidate.current_scheme() == self.scheme
                                       ])
            total_candidates = len(characteristic.candidates)
            output.append((f"{characteristic.value}", promoted_candidates, promoted_candidates/total_candidates))
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

            ))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

