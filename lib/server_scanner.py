from pathlib import Path
import os

'''
#this is a prototype of a function built to grab subject IDs from pheonix and send to asana
#path to jsons /data/predict/kcho/software/asana_pipeline/kevin/asana_project/tests/lib/test_PHOENIX/PROTECTED/PronetDC/raw/DC80354/surveys
#example caselist
'''

def grep_all_paths() -> list:
    #this will grab all paths through the files level,
    # right now the output is just the survey/.json because that is the only example file we have in there
    '''Grab all Pronet json paths and return them as a list of Path objects
    
    Notes:
        - right now the output is just the survey/.json because that is the
          only example file we have in there
    '''
    phoenix_dir = Path('/data/predict/kcho/software/asana_pipeline/kevin') / \
            'asana_project/tests/lib/test_PHOENIX'
    protected_dir = phoenix_dir / 'PROTECTED'
    subject_directories_under_phoenix = protected_dir.glob('*/*/*/*/*')
    for subject_id in subject_directories_under_phoenix:
        print(subject_id)
    return list(subject_directories_under_phoenix)


def grep_subject_files() -> list:
    #this will have the last directory as the subject id we want to grab
    subject_directories_under_phoenix = Path('/data/predict/kcho/software/asana_pipeline/kevin/asana_project/tests/lib/test_PHOENIX/PROTECTED').glob('*/*/*')
    for subject_id in subject_directories_under_phoenix:
        print(subject_id)
    return list(subject_directories_under_phoenix)


def grep_id_basename() -> str:
    id_path = '/data/predict/kcho/software/asana_pipeline/kevin/asana_project/tests/lib/test_PHOENIX/PROTECTED/PronetDC/raw/DC80354'
    basename_id = os.path.basename(id_path)
    return(basename_id)


def send_to_caselist(subject_id: str) -> str:
    #This function will take in subject_name and returns a list of subjects

    caselist = '/data/predict/kcho/software/asana_pipeline/kevin/asana_project/tests/lib/pheonix_caselist.txt'
    subject_id = grep_id_basename()

    with open(caselist, 'r') as fp:
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
        with open (caselist, 'a') as fp:
            fp.write(subject_id+'\n')
        return subject_id

caselist = '/data/predict/kcho/software/asana_pipeline/kevin/asana_project/tests/lib/pheonix_caselist.txt'
