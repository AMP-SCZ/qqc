from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ampscz_asana.models.mrizip import MriZip
from ampscz_asana.models.runsheet import MriRunSheet
from ampscz_asana.models.base import Base


class Subject(Base):
    __tablename__ = 'subject'

    subject_id = Column(String(255), primary_key=True)
    site = Column(String(255))
    network = Column(String(255))
    phoenix_mri_dir = Column(String(255))

    mri_zips = relationship("MriZip", backref="subject")
    mri_runsheets = relationship("MriRunSheet", backref="subject")

    baseline_runsheet_matched = Column(Boolean)
    followup_runsheet_matched = Column(Boolean)

    def __str__(self):
        return f"Subject({self.subject_id})"

    def __repr__(self):
        return self.__str__()
