from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ampscz_asana.models.base import Base


class MriRunSheet(Base):
    __tablename__ = 'mri_runsheet'

    id = Column(Integer, primary_key=True)
    run_sheet_num = Column(Integer)
    run_sheet_scan_date = Column(Date, nullable=True)
    run_sheet_session_num = Column(Integer, nullable=True)
    modified_time = Column(DateTime)
    subject_id = Column(String(255), ForeignKey('subject.subject_id'))
    session_num_id = Column(Integer, ForeignKey('session_num.id'))
    matching_date_in_zip = Column(Boolean, default=False)
    matching_date_and_ses_num = Column(Boolean, default=False)

    qqc = relationship("Qqc", backref="mri_runsheet", uselist=False)
    qqc = relationship("NoMri", backref="mri_runsheet", uselist=False)

    def __str__(self):
        return f"MriRunSheet({self.run_sheet_num} " \
               f"{self.run_sheet_scan_date} " \
               f"{self.run_sheet_session_num} " \
               f"{self.subject_id} " \
               f"{self.session_num_id} " \
               f"{self.matching_date_in_zip} " \
               f"{self.matching_date_and_ses_num})"

    def __repr__(self):
        return self.__str__()


class NoMri(Base):
    __tablename__ = 'no_mri'

    id = Column(Integer, primary_key=True)
    subject_id = Column(String(255), ForeignKey('subject.subject_id'))
    timepoint = Column(Integer)
    mri_run_sheet_id = Column(Integer, ForeignKey('mri_runsheet.id'))

    def __str__(self):
        return f"NoMri({self.subject_id} {self.timepoint})"

    def __repr__(self):
        return self.__str__()


class MissingMri(Base):
    __tablename__ = 'missing_mri'

    id = Column(Integer, primary_key=True)
    subject_id = Column(String(255), ForeignKey('subject.subject_id'))
    timepoint = Column(Integer)
    mri_run_sheet_id = Column(Integer, ForeignKey('mri_runsheet.id'))

    def __str__(self):
        return f"NoMri({self.subject_id} {self.timepoint})"

    def __repr__(self):
        return self.__str__()
