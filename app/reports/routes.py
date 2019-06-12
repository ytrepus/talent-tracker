from flask import request
from app.reports import reports_bp
from reporting.reports import PromotionReport


@reports_bp.route('/', methods=["POST", "GET"])
def reports():
    report_classes = {
        'promotions': PromotionReport
    }
    if request.method == "POST":
        form_data = request.form.to_dict()
        report_class = report_classes.get(form_data.pop('report-type'))
        params = form_data
        initialised_class = report_class(*params)
        return initialised_class.return_data("promotions-ethnicity-fls")
    return "Hello"
