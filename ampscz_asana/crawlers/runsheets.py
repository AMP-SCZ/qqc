import re
import pandas as pd
from pathlib import Path
from datetime import datetime
from ampscz_asana.models.subject import Subject
from ampscz_asana.models.runsheet import MriRunSheet
from ampscz_asana.crawlers.mrizip import match_mriZip



def add_run_sheets(db_session):
    # subject_objs = db_session.query(Subject).all()
    subjects = db_session.query(Subject)
    for subject_obj in subjects:
        mriRunSheets = get_mriRunSheets(db_session, subject_obj)


def get_info_from_rs(run_sheet_loc):
    run_sheet_df = pd.read_csv(run_sheet_loc)
    if not 'field name' in run_sheet_df.columns:
        if len(run_sheet_df) == 1:  # prescient
            run_sheet_df = run_sheet_df.T.reset_index()
            run_sheet_df.columns = ['field name', 'field_value']
        else:  # pronet
            run_sheet_df.columns = ['field name', 'field_value']

    run_sheet_df = run_sheet_df.set_index('field name')
    run_sheet_df = run_sheet_df.replace("-3", '')
    rs_scan_date = run_sheet_df.loc[
            'chrmri_entry_date'].field_value

    try:
        rs_scan_date = datetime.strptime(rs_scan_date, '%Y-%m-%d')
        rs_scan_date = str(rs_scan_date.strftime('%Y-%m-%d'))
    except:
        try:
            rs_scan_date = datetime.strptime(rs_scan_date.split(' ')[0],
                                             '%d/%m/%Y')
            rs_scan_date = str(rs_scan_date.strftime('%Y-%m-%d'))
        except AttributeError:
            rs_scan_date = ''
        except ValueError:  # when it's empty
            rs_scan_date = ''

    rs_session_num = run_sheet_df.loc[
            'chrmri_session_num'].field_value

    return (rs_scan_date, rs_session_num)


def get_mriRunSheets(db_session, subject_obj) -> list:
    run_sheets = Path(subject_obj.phoenix_mri_dir).glob('*sheet_mri*csv')
    for run_sheet in list(run_sheets):
        run_sheet_num = re.search(r'(\d).csv', run_sheet.name).group(1)
        modified_time = datetime.fromtimestamp(run_sheet.stat().st_mtime)

        existing_run_sheet = db_session.query(MriRunSheet).filter_by(
                subject_id=subject_obj.subject_id).filter_by(
                        run_sheet_num=run_sheet_num).filter_by(
                                modified_time=modified_time).first()
        if existing_run_sheet is None:
            # previous_run_sheet = db_session.query(MriRunSheet).filter_by(
                # subject_id=subject_obj.subject_id).filter_by(
                        # run_sheet_num=run_sheet_num).first()
            # db_session.delete(previous_run_sheet)
            rs_scan_date, rs_session_num = get_info_from_rs(run_sheet)
            print(rs_scan_date, rs_session_num)
            if rs_scan_date == '' or pd.isna(rs_scan_date):
                mriRunSheet = MriRunSheet(subject=subject_obj,
                                          run_sheet_num=run_sheet_num,
                                          modified_time=modified_time)
                db_session.add(mriRunSheet)
                db_session.commit()
                continue

            if rs_session_num == '' or pd.isna(rs_session_num):
                mriRunSheet = MriRunSheet(subject=subject_obj,
                                          run_sheet_num=run_sheet_num,
                                          run_sheet_scan_date=rs_scan_date,
                                          modified_time=modified_time)
                db_session.add(mriRunSheet)
                db_session.commit()
                continue
            # elif pd.isna(rs_scan_date) or pd.isna(rs_session_num):
                # mriRunSheet = MriRunSheet(subject=subject_obj,
                                          # run_sheet_num=run_sheet_num,
                                          # modified_time=modified_time)


            matching_date_in_zip, matching_date_and_ses_num, sessionNum = \
                    match_mriZip(db_session, subject_obj, rs_scan_date, rs_session_num)

            mriRunSheet = MriRunSheet(subject=subject_obj,
                                      run_sheet_num=run_sheet_num,
                                      run_sheet_scan_date=rs_scan_date,
                                      run_sheet_session_num=rs_session_num,
                                      modified_time=modified_time,
                                      session_num=sessionNum,
                                      matching_date_in_zip=matching_date_in_zip,
                                      matching_date_and_ses_num=matching_date_and_ses_num)
            print("MriRunSheet added:", mriRunSheet)
            db_session.add(mriRunSheet)
            db_session.commit()
