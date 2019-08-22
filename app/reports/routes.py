from flask import request, render_template
from app.reports import reports_bp
from reporting import ReportFactory
from reporting.detailed_report import DetailedReport
from app.models import Promotion


@reports_bp.route("/", methods=["POST", "GET"])
def reports():

    if request.method == "POST":
        form_data = request.form.to_dict()
        report = ReportFactory.create_report(
            report_type=form_data.pop("report-type"), **form_data
        )
        return report.return_data()
    return render_template("reports/select-report.html")


@reports_bp.route("/detailed", methods=["POST", "GET"])
def detailed_reports():
    if request.method == "POST":
        form_data = request.form.to_dict()
        report = DetailedReport(form_data.get('year'), form_data.get('scheme'), form_data.get('promotion-type'))
        return report.return_data()
    return render_template("reports/detailed-report.html", page_header="Detailed Report",
                           promotion_types=Promotion.query.all())
