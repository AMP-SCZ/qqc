import re
from ampscz_asana.models.subject import Subject
from ampscz_asana.models.session import SessionNum
from ampscz_asana.models.qqc import Qqc
from pathlib import Path


def add_qqc(db_session):
    MRI_ROOT = Path('/data/predict1/data_from_nda/MRI_ROOT')
    sessionNums = db_session.query(SessionNum).all()

    for sessionNum in sessionNums:
        sessionDate = sessionNum.session_date
        mriZip = sessionDate.mri_zip
        subject = mriZip.subject

        subject_id = subject.subject_id
        session_id_full = f'{sessionDate.session_date}' \
                          f'_{sessionNum.session_num}'
        session_id = re.sub('[-_]', '', session_id_full)

        sourcedata_dir = MRI_ROOT / 'sourcedata' / subject_id / \
                f'ses-{session_id}'
        rawdata_dir = MRI_ROOT / 'rawdata' / f'sub-{subject_id}' / \
                f'ses-{session_id}'
        qqc_dir = MRI_ROOT / 'derivatives' / 'quick_qc' / \
                f'sub-{subject_id}' / f'ses-{session_id}'
        qqc_output = qqc_dir / 'qqc_summary.html'

        existing_qqc = db_session.query(Qqc).filter_by(
                qqc_dir=str(qqc_dir)).first()
        if existing_qqc is not None:
            print(f'{subject_id} {session_id_full}: QQC already exists')
            continue

        qqc_executed = True if sourcedata_dir.is_dir() else False
        qqc_completed = True if qqc_output.is_file() else False
        
        qqc = Qqc(session_num_id = sessionNum.id,
                  qqc_executed = qqc_executed,
                  qqc_completed = qqc_completed,
                  sourcedata_dir = str(sourcedata_dir),
                  rawdata_dir = str(rawdata_dir),
                  qqc_dir = str(qqc_dir),
                  has_run_sheet = sessionNum.has_run_sheet,
                  session_num = sessionNum)

        existing_qqc = db_session.query(Qqc).filter_by(
                session_num_id=sessionNum.id).first()

        # Add subject if it doesn't exist
        if existing_qqc is None:
            print("QQC added:", qqc)
            db_session.add(qqc)
            db_session.commit()
        else:
            if qqc_completed is False:
                print("QQC updating:", qqc)
                existing_qqc.qqc_completed = qqc.qqc_completed
                existing_qqc.has_run_sheet = qqc.has_run_sheet
                existing_qqc.qqc_executed = qqc.qqc_executed
                db_session.commit()
            else:
                pass
