import sqlalchemy
from .db_session import SqlAlchemyBase


class Oil(SqlAlchemyBase):
    __tablename__ = 'oil'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    img = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    placed = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    coo = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
