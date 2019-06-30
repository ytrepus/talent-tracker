from reporting.base_report import Report
from reporting.promotion_reports import CharacteristicPromotionReport, BooleanCharacteristicPromotionReport, \
    DeltaOfferPromotionReport, MetaOfferPromotionReport


class ReportFactory:
    @staticmethod
    def create_report(report_type: str, **kwargs) -> Report:

        characteristic_reports = {key: CharacteristicPromotionReport for key in
                                  ['ethnicity', 'gender', 'working_pattern', 'age_range', 'belief', 'sexuality']}
        boolean_reports = {key: BooleanCharacteristicPromotionReport for key in
                           ['long_term_health_condition', 'caring_responsibility']}
        offer_reports = {'delta': DeltaOfferPromotionReport, 'meta': MetaOfferPromotionReport}
        promotion_reports = {**characteristic_reports, **boolean_reports, **offer_reports}
        reports = {"promotions": promotion_reports}

        report = reports.get(report_type).get(kwargs.get('attribute'))
        if not report:
            raise NotImplementedError("No such report type exists")
        else:
            return report(**kwargs)
