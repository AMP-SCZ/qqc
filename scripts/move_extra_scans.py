import os
import shutil
import json
import pandas as pd
import re
from pathlib import Path
import gspread
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from oauth2client.service_account import ServiceAccountCredentials


def get_series_number(json_file_loc:str):
    with open(json_file_loc, 'r') as fp:
        data = json.load(fp)
    
    return data['SeriesNumber']


def get_BIDS_file_with_session_num(rawdata_dir: Path,
                                   session_number: int) -> Path:
    # walk json files
    list_of_session_nums = []

    for root, dirs, files in os.walk(rawdata_dir):
        if Path(root).name == 'extra':
            continue
        for file in files:
            if file.endswith('.json'):
                session_num_found = get_series_number(Path(root) / file)
                list_of_session_nums.append(session_num_found)
                if int(session_num_found) == int(session_number):
                    print()
                    return Path(root) / file
                
    # print(list_of_session_nums, session_number)
    
    
def put_nifti_in_the_extra(rawdata_dir: Path) -> Path:
    extra_dir = rawdata_dir / 'extra'
    if not extra_dir.is_dir():
        return
    
    for json in extra_dir.glob('*json'):
        json_prefix = json.name.split('.json')[0]
        
        other_nifti_files = rawdata_dir.glob('*/*nii.gz')
        for other_nifti_file in other_nifti_files:
            if other_nifti_file.parent.name == 'extra':
                continue

            nifti_prefix = other_nifti_file.name.split('.nii.gz')[0]
            if json_prefix == nifti_prefix:
                print(f'Moving {other_nifti_file} to extra')
                shutil.move(other_nifti_file, extra_dir / other_nifti_file.name)
                
        # bval
        other_bval_files = rawdata_dir.glob('*/*bval')
        for other_bval_file in other_bval_files:
            if other_bval_file.parent.name == 'extra':
                continue

            bval_prefix = other_bval_file.name.split('.bval')[0]
            if json_prefix == bval_prefix:
                print(f'Moving {other_bval_file} to extra')
                shutil.move(other_bval_file, extra_dir / other_bval_file.name)        
                
        # bvec
        other_bval_files = rawdata_dir.glob('*/*bvec')
        for other_bval_file in other_bval_files:
            if other_bval_file.parent.name == 'extra':
                continue

            bval_prefix = other_bval_file.name.split('.bvec')[0]
            if json_prefix == bval_prefix:
                print(f'Moving {other_bval_file} to extra')
                shutil.move(other_bval_file, extra_dir / other_bval_file.name)        


def move_extra_scans():
    # Setup the Google Sheets API credentials
    scope = ["https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"]

    json_loc = "/data/predict1/home/nick/json_keys/gspread_official_key.json"
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_loc, scope)
    client = gspread.authorize(creds)

    # Open the Google Spreadsheet using its name
    sheet = client.open("U24 MRI QC").worksheet("Extra Series")

    # Get the values from the spreadsheet
    data = sheet.get_all_values()

    # Convert to pandas DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])

    # df = pd.read_csv('U24 MRI QC - Extra Series (3).csv')
    df = df[~df['Certain (1: certain, 2: assumed)'].isnull()]
    df['site'] = df['sub_id_gs'].str[:2]

    df['Series in issue'] = df['Series in issue'].str.replace('func', 'fmri')
    df['Series in issue'] = df['Series in issue'].str.replace('dmri', 'dwi')
    df['Series in issue'] = df['Series in issue'].str.replace('anat', 'T1w')
    df['issue_in_fmri'] = df['Series in issue'].str.contains(
            'fMRI', flags=re.IGNORECASE)
    df['issue_in_dwi'] = df['Series in issue'].str.contains(
            'dwi', flags=re.IGNORECASE)
    df['issue_in_t1w'] = df['Series in issue'].str.contains(
            't1w', flags=re.IGNORECASE)
    df['issue_in_t2w'] = df['Series in issue'].str.contains(
            't2w', flags=re.IGNORECASE)
    df['issue_in_fmap'] = df['Series in issue'].str.contains(
            'fmap', flags=re.IGNORECASE)



    print(df.groupby('Certain (1: certain, 2: assumed)').count()[
                ['sub_id_gs']])


    print(df[df['Certain (1: certain, 2: assumed)']==2].groupby(
        'site').count()[['sub_id_gs']].sort_values(
            'sub_id_gs',
            ascending=False))


    print(df[~df['Confirmed from data'].isnull()][[
        'sub_id_gs', 'ses_id_gs', 'Confirmed from data']])


    df['number_of_series_to_move'] = df['Series Number to remove'].apply(
            lambda x: len(str(x).split(',')))


    for index, row in df.iterrows():
        certain = row['Certain (1: certain, 2: assumed)']
        if pd.isna(row['Series Number to remove']):
            continue
        
        if row['Series Number to remove'] == '':
            continue
            
        if certain != '1':
            print(row, 'is not certain')
            print()
            continue

        print(f'{row["sub_id_gs"]} {row["ses_id_gs"]}')
        for series_to_remove in row['Series Number to remove'].split(','):
            full_path = get_BIDS_file_with_session_num(
                    row['rawdata_location_gs'],
                    series_to_remove)
            full_path

            if full_path is None:
                print(f'Already moved')
                continue

            command = f'\tremoving Series {series_to_remove} ({full_path.name}) of {row["Series in issue"]} to extra'
            print(command)

            new_loc = full_path.parent.parent / 'extra' / full_path.name
            new_loc.parent.mkdir(exist_ok=True)

            if full_path != new_loc:
                command = f'\tmv {full_path} {new_loc}'
                print(command)
                shutil.move(full_path, new_loc)
                
            put_nifti_in_the_extra(Path(row['rawdata_location_gs']))
            

if __name__ == '__main__':
    move_extra_scans()
