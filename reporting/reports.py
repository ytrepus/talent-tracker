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
        pass

    def return_data(self, filename: str):
        headers = Headers()
        headers["Content-Disposition"] = f"attachment; filename={filename}.csv"
        headers["Content-type"] = "text/csv"

        return Response(
            stream_with_context(self.generate_report_data()),
            mimetype='text/csv', headers=headers
        )


class PromotionReport(Report):
    def __init__(self, characteristic: str, scheme: str):
        super().__init__()
        self.table = self.tables.get(characteristic)
        self.scheme = Scheme.query.filter_by(name=f'{scheme}')
        self.headers = ['characteristic', 'number promoted', 'percentage promoted']

    def generate_report_data(self):
        # output = [
        #     ('white', .5, 90),
        #     ('bame', .33, 5),
        # ]
        """
        Search for promoted candidates and group them by characteristic. Provide an absolute number promoted
        and the percentage of that group promoted
        :return:
        :rtype:
        """

        output = []
        selected_characteristic = self.table.query.all()
        for characteristic in selected_characteristic:
            output.append([characteristic, 'word', 'word'])

        data = StringIO()
        w = csv.writer(data)

        # write header
        w.writerow(('characteristic', 'percentage promoted', 'number promoted'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        # write each item
        for item in output:
            w.writerow((
                item[0],
                "{0:.0%}".format(item[1]),  # format decimal as percentage
                item[2]
            ))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

