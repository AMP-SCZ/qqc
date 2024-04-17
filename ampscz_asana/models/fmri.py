from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ampscz_asana.models.base import Base


class fMRI(Base):
    __tablename__ = 'fMRI'

    id = Column(Integer, primary_key=True)
    qqc_id = Column(Integer, ForeignKey('qqc.id'))
    ap1 = Column(Boolean)
    pa1 = Column(Boolean)
    ap2 = Column(Boolean)
    pa2 = Column(Boolean)


class fMRIPrep(Base):
    __tablename__ = 'fMRI_fmriprep'

    id = Column(Integer, primary_key=True)
    fmri_id = Column(Integer, ForeignKey('fMRI.id'))
    fmriprep_data = Column(Boolean)
