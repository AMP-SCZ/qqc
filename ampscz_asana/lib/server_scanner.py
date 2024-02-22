import re
import os
import json
import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict
from datetime import datetime


logger = logging.getLogger(__name__)

'''
#this is a prototype of a function built to grab subject IDs from pheonix and send to asana
#path to jsons /data/predict/kcho/software/asana_pipeline/kevin/asana_project/tests/lib/test_PHOENIX/PROTECTED/PronetDC/raw/DC80354/surveys
#example caselist
'''

def get_most_recent_file(root: Path,
                         file_prefix: str = 'df_to_dpdash_',
                         date_format: str = '%Y_%m_%d') -> Path:
    '''Get most recently created file based on the date in the file name'''
    files = root.glob(f'{file_prefix}*')

    most_recent_date = datetime.strptime('1990_01_01', date_format)
    most_recent_file = ''
    for file in files:
        date_str = re.search('(\d{4}_\d{1,2}_\d{1,2})', file.name).group(1)
        date_time = datetime.strptime(date_str, date_format)
        if date_time > most_recent_date:
            most_recent_date = date_time
            most_recent_file = file

    return most_recent_file


def get_all_eeg_zip(phoenix_root: Path, **kwargs) -> list:
    # PHOENIX/PROTECTED/PronetIR/raw/IR01451/eeg/IR01451.Pronet.Run_sheet_eeg_2.csv
    test = kwargs.get('test', False)
    if test:
        prefix = 'PROTECTED/*YA/raw/YA16*/eeg/*[zZ][iI][pP]'
    else:
        prefix = 'PROTECTED/*/raw/*/mri/*[zZ][iI][pP]'

    zip_files = list(phoenix_root.glob(prefix))

    return zip_files



def get_all_mri_zip(phoenix_root: Path, **kwargs) -> list:
    # PHOENIX/PROTECTED/PronetIR/raw/IR01451/eeg/IR01451.Pronet.Run_sheet_eeg_2.csv
    test = kwargs.get('test', False)
    if test:
        prefix = 'PROTECTED/*NC/raw/NC02111/mri/[!.]*_MR_*[zZ][iI][pP]'
    else:
        prefix = 'PROTECTED/*/raw/*/mri/[!.]*_MR_*[zZ][iI][pP]'

    zip_files = list(phoenix_root.glob(prefix))

    return zip_files


def get_all_subjects_with_consent(phoenix_root: Path) -> list:
    metadata_files = (phoenix_root / 'GENERAL').glob('*/*metadata.csv')
    subject_ids = []
    for metadata_file in metadata_files:
        if metadata_file.parent.name == (metadata_file.name + '_metadata.csv'):
            df = pd.read_csv(metadata_file)
            subject_ids += df['Subject ID'].tolist()
        
    return subject_ids


def get_site_network_dict(phoenix_roots) -> dict:
    '''Get site network matching dictionary'''
    metadata_files = []
    for phoenix_root in phoenix_roots:
        metadata_files += list((phoenix_root / 'GENERAL').glob(
            '*/*metadata.csv'))

    site_net_dict = {}

    for metadata_file in metadata_files:
        network_dir = metadata_file.parent.name
        network = 'Prescient' if 'Prescient' in network_dir else 'Pronet'
        site = network_dir[-2:]
        site_net_dict[site] = network

    return site_net_dict


def grep_run_sheets(phoenix_dir: Path,
                    subject: str = None,
                    test: bool = False) -> list:
    '''Grab run sheets from PHOENIX'''
    logger.info(f'Searching run sheets under {phoenix_dir}')
    if subject is None:
        subject = '*'
    protected_dir = phoenix_dir / 'PROTECTED'
    if test:
        subject_directories_under_phoenix = protected_dir.glob(
                '*[YM][AE]/raw/*12*/[em][er][gi]/*Run_sheet*csv')
                # '*[YM][AE]/raw/*/[em][er][gi]/*Run_sheet*csv')
    else:
        subject_directories_under_phoenix = protected_dir.glob(
                f'*/raw/{subject}/[em][er][gi]/*Run_sheet*csv')
    return list(subject_directories_under_phoenix)


def grep_all_paths(phoenix_dir: Path) -> list:
    #this will grab all paths through the files level,
    # right now the output is just the survey/.json because that is the only example file we have in there
    '''Grab all Pronet json paths and return them as a list of Path objects
    
    Notes:
        - right now the output is just the survey/.json because that is the
          only example file we have in there
    '''
    protected_dir = phoenix_dir / 'PROTECTED'
    subject_directories_under_phoenix = protected_dir.glob('*/*/*/*/*')
    for subject_id in subject_directories_under_phoenix:
        print(subject_id)
    return list(subject_directories_under_phoenix)


def grep_subject_files(phoenix_dir: Path) -> list:
    #this will have the last directory as the subject id we want to grab
    subject_directories_under_phoenix = list((phoenix_dir / 'PROTECTED').glob('*/*/*'))
    basename_lines = []
    for subject_id in subject_directories_under_phoenix:
        basename_lines.append(grep_id_basename(subject_id))
    return basename_lines


def grep_id_basename(id_path: Path) -> str:
    basename_id = os.path.basename(id_path)
    return basename_id


def send_to_caselist(subject_id: str, phoenix_database: str) -> str:
    #This function will take in subject_name and returns a list of subjects

    with open(phoenix_database, 'r') as fp:
        subject_lines_with_strip = fp.readlines()
        subject_lines = []
        for subject_line in subject_lines_with_strip:
            subject_lines.append(subject_line.strip())

    if subject_id in subject_lines:
        print('this subject has already been backed up!')
        return None

    else:
        print('this subject is new. it  will be backed up.')
        subject_lines.append(subject_id)
        with open (phoenix_database, 'a') as fp:
            fp.write(subject_id+'\n')
        return subject_id


def consent_date_extraction(ampscz_id: str, phoenix_root: Path) -> str:
    '''Get consent date string for a given Pronet AMP-SCZ subject'''
    site = ampscz_id[:2]
    json_file_path = phoenix_root / 'PROTECTED' / f'Pronet{site}' / \
            'raw' / ampscz_id / 'surveys' / f'{ampscz_id}.Pronet.json'

    with open(json_file_path, 'r') as fp:
        json_data = json.load(fp)
    consent_date = json_data[0]['chric_consent_date']
    return consent_date


def consent_date_extraction_csv(ampscz_id: str, phoenix_root: Path) -> str:
    '''Get consent date string for a given Prescient AMP-SCZ subject'''
    site = ampscz_id[:2]
    csv_file_path = phoenix_root / 'PROTECTED' / f'Prescient{site}' / \
        'raw' / ampscz_id / 'surveys' / \
        f'{ampscz_id}_informed_consent_run_sheet.csv'
    df = pd.read_csv(csv_file_path)
    
    assert len(df) == 1  # make sure there is only one row in the consent csv file
    consent_date = df['chric_consent_date'].iloc[0]

    return consent_date


class MoreThanOneSubjectIdError(Exception):
    pass

class SubjectIdMissingInVisitStatus(Exception):
    pass


def get_subject_timepoint(visit_df, subject_id: str) -> str:
    '''Get subject timepoint using formqc outputs'''
    subject_df = visit_df[visit_df.subjectid == subject_id]

    if len(subject_df) > 1:
        logger.warning(f'{subject_id} has more than one line in visit status')
        raise MoreThanOneSubjectIdError
    elif len(subject_df) == 0:
        logger.warning(f'{subject_id} not in visit status')
        raise SubjectIdMissingInVisitStatus

    return (subject_df.iloc[0]['visit_status_string'],
            subject_df.iloc[0]['last_visit_status'])


def get_visit_df(formqc_loc: str = '/data/predict1/data_from_nda/formqc') \
        -> pd.DataFrame:
    formsqc_path = Path(formqc_loc)
    visit_status_file = formsqc_path / 'combined-AMPSCZ-screening-day1to1.csv'
    df = pd.read_csv(visit_status_file)
    columns = ['subjectid', 'visit_status_string', 'last_visit_status']
    return df[columns]


def return_matching_visit_status(subjects: List[str]) -> Dict[str, tuple]:
    subject_visit_dict = {}
    visit_df = get_visit_df()
    for subject in subjects:
        try:
            subject_visit_dict[subject] = get_subject_timepoint(visit_df,
                                                                subject)
        except SubjectIdMissingInVisitStatus:
            subject_visit_dict[subject] = ('unknown', 'unknown')

    return subject_visit_dict
        

if __name__ == '__main__':
    print('Beginning of the Simone pipeline')
    subject_files_list = grep_subject_files()

    for subject_id in subject_files_list:
        potential_subject = send_to_caselist(subject_id)
        print(potential_subject)

    print("Completed")
