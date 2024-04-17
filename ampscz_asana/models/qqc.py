from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ampscz_asana.models.base import Base


class Qqc(Base):
    __tablename__ = 'qqc'
    id = Column(Integer, primary_key=True)
    session_num_id = Column(Integer, ForeignKey('session_num.id'))
    mri_runsheet_id = Column(Integer, ForeignKey('mri_runsheet.id'))
    qqc_executed = Column(Boolean, default=False)
    qqc_completed = Column(Boolean, default=False)
    sourcedata_dir = Column(String(255))
    rawdata_dir = Column(String(255))
    qqc_dir = Column(String(255))
    has_run_sheet = Column(Boolean, default=False)

    dwi = relationship("Dwi", backref="qqc")

    def __str__(self):
        return f"Qqc({self.sourcedata_dir})"

    def __repr__(self):
        return self.__str__()
