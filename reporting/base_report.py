import csv
from abc import ABC, abstractmethod
from io import StringIO

from flask import Response, stream_with_context
from werkzeug.datastructures import Headers

from app.models import Scheme


class Report(ABC):
    """
    This is the base report. All reports should be subclassed from it. They should implement the abstract methods but
    should not override any of the others.
    """

    def __init__(self, scheme: str):
        self.scheme: Scheme = Scheme.query.filter_by(name=f"{scheme}").first()
        self.filename = None
        self.headers = []

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
            mimetype="text/csv",
            headers=headers,
        )
