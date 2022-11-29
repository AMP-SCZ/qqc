from typing import List
from pathlib import Path
import sys
import pandas as pd
import qqc
data_loc = Path(qqc.__file__).parent.parent / 'data'
# from pronet_run_sheet import var
from qqc.pronet_run_sheet import var


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
