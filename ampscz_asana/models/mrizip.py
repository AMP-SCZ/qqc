from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ampscz_asana.models.base import Base


class MriZip(Base):
    __tablename__ = 'mri_zip'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255))
    modified_time = Column(DateTime)
    wrong_format = Column(Boolean, default=False)
    removed = Column(Boolean, default=False)
    subject_id = Column(String(255), ForeignKey('subject.subject_id'))
    session_date = relationship("SessionDate",
                                backref="mri_zip",
                                uselist=False)

    def __str__(self):
        return f"MriZip({self.subject_id} {self.filename})"

    def __repr__(self):
        return self.__str__()


