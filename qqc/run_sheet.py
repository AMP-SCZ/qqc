from typing import List
from pathlib import Path
import sys
import pandas as pd
import qqc
data_loc = Path(qqc.__file__).parent.parent / 'data'
# from pronet_run_sheet import var
from qqc.pronet_run_sheet import var


def get_matching_run_sheet_path(mri_data: str, session_str: str) -> Path:
    '''Get matching run sheet csv file path

    Read all existing run sheet files and return the path of the matching
    run sheet to the given session string.

    Key arguments:
        mri_data: location of lochness transferred MRI data root or zip file,
                  str.
                  'PHOENIX/PROTECTED/PronetAA/raw/AB012345/mri/' \
                          'AB012345_MR_2022_09_20_1'
        session_str: date and session stated in the MRI directory or file, str.
                     eg: '2022_09_20_1'

    Returns:
        csv: path of the matching CSV file
    '''
    run_sheet = Path('no_run_sheet')
    for run_sheet_tmp in Path(mri_data).parent.glob('*Run_sheet_mri*.csv'):
        run_sheet_df_tmp = pd.read_csv(run_sheet)
        run_sheet_dict = run_sheet_df_tmp.set_index('field name').loc[
                ['chrmri_session_num',
                 'chrmri_session_year',
                 'chrmri_session_month',
                 'chrmri_session_day']].to_dict()
        sp = session_str.split('_')
        if run_sheet_dict['chrmri_session_num'] == sp[-1] and \
                run_sheet_dict['chrmri_session_year'] == sp[0] and \
                run_sheet_dict['chrmri_session_month'] == sp[1] and \
                run_sheet_dict['chrmri_session_day'] == sp[2]:
            run_sheet = run_sheet_tmp
            break

    return run_sheet


def get_run_sheet(run_sheet: Path):
    print(f'Using run sheet {run_sheet}')
    run_sheet_df = pd.read_csv(run_sheet)

    if not 'field name' in run_sheet_df.columns:
        if len(run_sheet_df) == 1:  # prescient
            run_sheet_df = run_sheet_df.T.reset_index()
            run_sheet_df.columns = ['field name', 'field value']
        else:  # pronet
            run_sheet_df.columns = ['field name', 'field value']

    run_sheet_df['field label'] = run_sheet_df['field name'].apply(
            lambda x: get_dict_from_pronet_dict_list(
                x, var))
    run_sheet_df = run_sheet_df[
            ['field name', 'field label', 'field value']]

    return run_sheet_df


def get_dict_from_pronet_dict_list(field_name,
                                   pronet_run_sheet_dicts: List[dict]) -> str:
    '''Extract field label for given field name from the Pronet dict list

    Key Argument:
        field_name: field name, str.
        pronet_run_sheet_dicts: List of dictionaries, list.

    Returns:
        field label, str
    '''
    for field_dict in pronet_run_sheet_dicts:
        if field_dict['field_name'] == field_name:
            return field_dict['field_label']

    return 'No matching label for this item in DB'
