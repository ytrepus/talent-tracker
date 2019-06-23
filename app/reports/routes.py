from flask import request, render_template
from app.reports import reports_bp
from reporting.reports import CharacteristicPromotionReport, BooleanCharacteristicPromotionReport


@reports_bp.route('/', methods=["POST", "GET"])
def reports():

    def promotion_report_type(string_from_form):
        characteristic_reports = ['ethnicity', 'gender', 'working-pattern', 'age-range', 'belief', 'sexuality']
        boolean_reports = ['long_term_health_condition', 'caring_responsibility']
        if string_from_form in characteristic_reports:
            return CharacteristicPromotionReport
        elif string_from_form in boolean_reports:
            return BooleanCharacteristicPromotionReport

    report_classes = {
        'promotions': promotion_report_type
    }

    if request.method == "POST":
        form_data = request.form.to_dict()
        report_type = report_classes.get(form_data.pop('report-type'))
        report_class = report_type(form_data.get('attribute'))
        params = form_data
        initialised_class = report_class(**params)
        return initialised_class.return_data()
    return render_template("reports/select-report.html")
