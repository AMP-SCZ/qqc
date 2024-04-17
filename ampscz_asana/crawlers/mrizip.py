from ampscz_asana.models.subject import Subject
from ampscz_asana.models.mrizip import MriZip
from pathlib import Path


def update_mri_zip(db_session):
    mriZips = db_session.query(MriZip).all()
    for mriZip in mriZips:
        subject = mriZip.subject
        file_loc = Path(subject.phoenix_mri_dir) / mriZip.filename
        if not file_loc.is_file():
            db_session(mriZip.session_date.session_num)
            db_session(mriZip.session_date)
            db_session.delete(mriZip)
    db_session.commit()


def match_mriZip(db_session, subject_obj, rs_scan_date, rs_session_num) -> tuple:
    for mriZip in subject_obj.mri_zips:
        try:
            zip_session_date = mriZip.session_date.session_date
        except AttributeError:
            continue

        for sessionNum in mriZip.session_date.session_num:
            try:
                zip_session_num =  sessionNum.session_num
            except AttributeError:
                continue

            if str(zip_session_date) == str(rs_scan_date) and \
                    str(zip_session_num) == str(rs_session_num):
                print('matched******************')
                sessionNum.has_run_sheet = True
                db_session.commit()
                return (True, True, sessionNum)

        for sessionNum in mriZip.session_date.session_num:
            try:
                zip_session_num =  sessionNum.session_num
            except AttributeError:
                continue

            if str(zip_session_date) == str(rs_scan_date):
                return (True, False, None)

    return (False, False, None)
