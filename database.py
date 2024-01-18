import datetime
import sqlalchemy
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, DateTime

engine = sqlalchemy.create_engine('sqlite:///data/point.sqlite3', echo=False)
Base = declarative_base()


class Point(Base):
    __tablename__ = "point"

    id = Column(Integer, primary_key=True, autoincrement=True)

    group_id = Column(Integer)

    ap1_rtt = Column(Integer)
    ap2_rtt = Column(Integer)
    ap3_rtt = Column(Integer)
    ap4_rtt = Column(Integer)

    created_at = Column(DateTime)


def update_point(point_data):
    session = sessionmaker(bind=engine)()

    point = Point()

    point.group_id = point_data["group_id"]

    point.ap1_rtt = point_data["ap1_rtt"]
    point.ap2_rtt = point_data["ap2_rtt"]
    point.ap3_rtt = point_data["ap3_rtt"]
    point.ap4_rtt = point_data["ap4_rtt"]

    point.created_at = datetime.datetime.now()

    session.merge(point)
    session.commit()

    session.close()


def get_rtt():
    session = sessionmaker(bind=engine)()
    points = session.query(
        Point.group_id,
        Point.ap1_rtt,
        Point.ap2_rtt,
        Point.ap3_rtt,
        Point.ap4_rtt
    ).all()
    session.close()

    return points