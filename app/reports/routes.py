from flask import request, render_template
from app.reports import reports_bp
from reporting.reports import EthnicityPromotionReport


@reports_bp.route('/', methods=["POST", "GET"])
def reports():
    report_classes = {
        'promotions': {
            'ethnicity': EthnicityPromotionReport,
        }
    }
    if request.method == "POST":
        form_data = request.form.to_dict()
        report_class = report_classes.get(form_data.pop('report-type')).get(form_data.pop('characteristic'))
        params = form_data
        initialised_class = report_class(**params)
        return initialised_class.return_data()
    return render_template("reports/select-report.html")
