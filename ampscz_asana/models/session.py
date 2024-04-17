from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ampscz_asana.models.base import Base


class SessionDate(Base):
    __tablename__ = 'session_date'

    id = Column(Integer, primary_key=True)
    session_date = Column(Date)
    zip_id = Column(Integer, ForeignKey('mri_zip.id'))

    # # relationship to mri zip
    # mri_zip = relationship("MriZip", back_populates="session_date")
    # session_num_id = Column(Integer, ForeignKey('session_num.id'))
    session_num = relationship("SessionNum", backref="session_date")

    def __str__(self):
        return f"SessionDate({self.session_date})"

    def __repr__(self):
        return self.__str__()


class SessionNum(Base):
    __tablename__ = 'session_num'

    id = Column(Integer, primary_key=True)
    session_num = Column(Integer)
    session_id = Column(Integer, ForeignKey('session_date.id'))
    has_run_sheet = Column(Boolean, default=False)

    mri_runsheet = relationship("MriRunSheet",
                                uselist=False,
                                backref="session_num")
    qqc = relationship("Qqc",
                       uselist=False,
                       backref="session_num")

    def __str__(self):
        return f"SessionNum({self.session_num} {self.has_run_sheet})"

    def __repr__(self):
        return self.__str__()


