from app import db
from app.models import FLSLeadership


class TestLeadership:
    f = FLSLeadership(
        increased_visibility=5,
        confident_leader=4,
        inspiring_leader = 3,
        when_new_role = "As soon as possible",
        confidence_built = 5,
        application_id = 1
    )
    db.session.add(f)
    db.session.commit()
    assert True
