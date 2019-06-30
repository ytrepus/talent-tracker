from flask import request, render_template
from app.reports import reports_bp
from reporting.reports import ReportFactory


@reports_bp.route('/', methods=["POST", "GET"])
def reports():

    if request.method == "POST":
        form_data = request.form.to_dict()
        report = ReportFactory.create_report(report_type=form_data.pop('report-type'), **form_data)
        return report.return_data()

    return render_template("reports/select-report.html")
