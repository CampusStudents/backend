from src.db.db_helper import db_helper
from src.db.unit_of_work import UnitOfWork


def get_unit_of_work() -> UnitOfWork:
    return UnitOfWork(db_helper.session_factory)
