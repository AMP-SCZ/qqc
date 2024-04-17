import re
from pathlib import Path
from datetime import datetime
from ampscz_asana.models.subject import Subject
from ampscz_asana.models.session import SessionDate, SessionNum
from ampscz_asana.models.mrizip import MriZip
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect


def add_session_date(db_session):
    subject_objs = db_session.query(Subject).all()
    for subject_obj in subject_objs:

        mriZips_list = db_session.query(MriZip).filter_by(
                subject_id=subject_obj.subject_id).all()

        zip_files = Path(subject_obj.phoenix_mri_dir).glob('*.[Zz][Ii][Pp]')
        sessionDates = []
        for zip_file in zip_files:
            if 'checksum' in zip_file.name:
                continue

            if zip_file.name in [x.filename for x in mriZips_list]:
                print('ZipFile already added:',  zip_file.name)
                continue

            modified_time = datetime.fromtimestamp(zip_file.stat().st_mtime)
            mriZip = MriZip(filename=zip_file.name,
                            modified_time=modified_time,
                            subject=subject_obj)
            db_session.add(mriZip)
            db_session.commit()
            print("Zip file added:", mriZip)

            # search date
            date_search = re.search('\d{4}_\d{2}_\d{2}', zip_file.name)
            if date_search:
                date_str = date_search.group(0)
                try:
                    datetime.strptime(date_str, '%Y_%m_%d')
                except ValueError:
                    print('wrong date')
                    mriZip.wrong_format = True
                    db_session.commit()
                    continue

                sessionDate = SessionDate(session_date=date_str,
                                          mri_zip=mriZip)
                db_session.add(sessionDate)
                db_session.commit()
                sessionDates.append(sessionDate)
            else:
                mriZip.wrong_format = True
                db_session.commit()

        for sessionDate in sessionDates:
            mriZip = db_session.query(MriZip).filter_by(id=sessionDate.zip_id).first()
            session_num_search = re.search('\d{4}_\d{2}_\d{2}_(\d+)\.',
                                           mriZip.filename)
            if session_num_search:
                session_num_str = session_num_search.group(1)
                sessionNum = SessionNum(session_num=session_num_str,
                                        session_date=sessionDate)
                mriZip.wrong_format = False
                db_session.add(sessionNum)
                db_session.commit()
            else:
                mriZip.wrong_format = True
                db_session.commit()

