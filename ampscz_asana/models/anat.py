from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ampscz_asana.models.base import Base


class Anat(Base):
    __tablename__ = 'anat'

    id = Column(Integer, primary_key=True)
    qqc_id = Column(Integer, ForeignKey('qqc.id'))
    t1w_data = Column(Boolean)
    t2w_data = Column(Boolean)


class Mriqc(Base):
    __tablename__ = 'anat_mriqc'

    id = Column(Integer, primary_key=True)
    anat_id = Column(Integer, ForeignKey('anat.id'))
    t1w_data = Column(Boolean)
    t2w_data = Column(Boolean)


class Freesurfer(Base):
    __tablename__ = 'anat_freesurfer'

    id = Column(Integer, primary_key=True)
    anat_id = Column(Integer, ForeignKey('anat.id'))
    freesurfer_data = Column(Boolean)
