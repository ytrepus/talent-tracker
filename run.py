from app import create_app
from app.models import Role, User, Candidate, Organisation, db

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role, 'Candidate': Candidate, 'Organisation': Organisation}
