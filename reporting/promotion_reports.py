from app.models import Ethnicity, Gender, Candidate, Sexuality, WorkingPattern, Belief, AgeRange

from reporting.base_promotion_report import PromotionReport


class CharacteristicPromotionReport(PromotionReport):
    """
    This class is for reports that iterate over a separate table. The tables are listed in self.tables. This report
    iterates over each value in the table and groups together candidates with that value
    """
    def __init__(self, scheme: str, year: str, attribute: str):
        super().__init__(scheme, year, attribute)
        self.tables = {'ethnicity': Ethnicity, 'gender': Gender, 'sexuality': Sexuality, 'belief': Belief,
                       'working_pattern': WorkingPattern, 'age_range': AgeRange}
        self.table = self.tables.get(self.attribute)

    def get_row_metadata(self):
        return [(row.value, self.candidates_with_characteristic(row)) for row in self.table.query.all()]

    def candidates_with_characteristic(self, characteristic):
        return [candidate for candidate in self.eligible_candidates()
                if getattr(candidate, self.attribute) == characteristic]


class BooleanCharacteristicPromotionReport(PromotionReport):
    """
    These reports are those where the corresponding database field is a boolean, rather than a distinct table.
    """
    def __init__(self, scheme: str, year: str, attribute: str):
        super().__init__(scheme, year, attribute)
        self.human_readable_characteristics = {
            'long_term_health_condition': {
                True: "People with a disability", False: "People without a disability", None: "No answer provided"
            },
            'caring_responsibility': {
                True: "I have caring responsibilities", False: "I do not have caring responsibilities",
                None: "No answer provided"
            }
        }
        self.human_readable_row_titles = self.human_readable_characteristics.get(self.attribute)

    def get_row_metadata(self):
        return [
            (value, Candidate.query.filter(getattr(Candidate, self.attribute).is_(key)).all())
            for key, value in self.human_readable_row_titles.items()
        ]


class OfferPromotionReport(PromotionReport):
    def __init__(self, scheme, year, attribute):
        super().__init__(scheme, year, attribute)
        self.upper_attribute = attribute.upper()
        self.human_readable_row_titles = {
            True: f"Candidates eligible for {self.upper_attribute}",
            False: f"Candidates on {self.upper_attribute}"
        }

    def get_row_metadata(self):
        return [
            (f"Candidates eligible for {self.upper_attribute}", self.eligible_candidates()),
            (f"Candidates on {self.upper_attribute}", self.candidates_on_offer(self.attribute)),
            (f"Candidates not on {self.upper_attribute}",
             list(set(self.eligible_candidates()) - set(self.candidates_on_offer(self.attribute))))
        ]

    def candidates_on_offer(self, offer):
        return [candidate for candidate in super().eligible_candidates() if getattr(candidate.applications[0], offer)]


class MetaOfferPromotionReport(OfferPromotionReport):
    def __init__(self, scheme, year, attribute):
        super().__init__(scheme, year, attribute)

    def eligible_candidates(self):
        return [candidate for candidate in super().eligible_candidates() if candidate.ethnicity.bame]


class DeltaOfferPromotionReport(OfferPromotionReport):
    def __init__(self, scheme, year, attribute):
        super().__init__(scheme, year, attribute)

    def eligible_candidates(self):
        return [candidate for candidate in super().eligible_candidates() if candidate.long_term_health_condition]
