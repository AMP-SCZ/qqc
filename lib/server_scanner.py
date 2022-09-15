from pathlib import Path
import os
import json
import pandas as pd 

'''
#this is a prototype of a function built to grab subject IDs from pheonix and send to asana
#path to jsons /data/predict/kcho/software/asana_pipeline/kevin/asana_project/tests/lib/test_PHOENIX/PROTECTED/PronetDC/raw/DC80354/surveys
#example caselist
'''

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



if __name__ == '__main__':
    print('Beginning of the Simone pipeline')
    subject_files_list = grep_subject_files()

    for subject_id in subject_files_list:
        potential_subject = send_to_caselist(subject_id)
        print(potential_subject)

    print("Completed")
