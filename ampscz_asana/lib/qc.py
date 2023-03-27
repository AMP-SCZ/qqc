from ampscz_asana.lib.server_scanner import grep_run_sheets
import re
import pandas as pd
from pathlib import Path
from ampscz_asana.lib.utils import convert_AU_to_US_date
from datetime import datetime
import os
import math
import json

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

phoenix_dir = Path('/data/predict1/data_from_nda/Pronet/PHOENIX')
phoenix_dir = Path('/data/predict1/data_from_nda/Prescient/PHOENIX')


def get_entry_date_from_run_sheet(run_sheet: Path) -> str:
    ''''return entry date from the run sheet'''
    if 'Prescient' in str(run_sheet):
        df = pd.read_csv(run_sheet).T.reset_index()
        df.columns = ['field_name', 'field_value']
    else:
        df = pd.read_csv(run_sheet)

    entry_date = df.set_index('field_name').loc['chrmri_entry_date',
                                                'field_value']
    if pd.isna(entry_date):
        return ''
    
    if 'Prescient' in str(run_sheet):
        entry_date = convert_AU_to_US_date(entry_date)

    entry_date = re.sub('-', '_', entry_date)

    return entry_date


def check_mri_data(run_sheet: Path, entry_date: str) -> bool:
    ''''return if there is MR data and entry date'''
    if entry_date == '':
        return False

    # pronet
    for i in run_sheet.parent.glob(f'*{entry_date}*'):
        if i.is_dir():
            print(i)
            return True

    # prescient
    for i in run_sheet.parent.glob(f'*{entry_date}*.[Zz][Ii][Pp]'):
        return True

    return False


def check_when_transferred(subject: str, entry_date: str) -> bool:
    ''''return if there is MR data and entry date'''
    mri_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    source_root = mri_root / 'sourcedata'
    date_numbers_only = re.sub('[-_]', '', entry_date)
    subject_dir = source_root / subject
    qqc_first_outputs = list(subject_dir.glob(f'*{date_numbers_only}*'))

    if len(qqc_first_outputs) >= 1:
        qqc_first_output = qqc_first_outputs[0]
        ctime = qqc_first_output.stat().st_ctime
        date_str = datetime.fromtimestamp(ctime).strftime('%Y-%m-%d')
        return date_str


def is_qqc_executed(subject, entry_date) -> bool:
    mri_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    source_root = mri_root / 'sourcedata'

    date_numbers_only = re.sub('[-_]', '', entry_date)
    print(date_numbers_only)
    subject_dir = source_root / subject
    qqc_first_outputs = subject_dir.glob(f'*{date_numbers_only}*')

    if len(list(qqc_first_outputs)) >= 1:
        return True
    else:
        return False

    
def date_of_zip(subject, entry_date, phoenix_dir):
    formatted_entry_date = entry_date.replace("-", "_")
    if 'Pronet' in phoenix_dir:
        prefix = 'Pronet'
    else:
        prefix = 'Prescient'
    base_dir = Path(f'/data/predict1/data_from_nda/{prefix}/PHOENIX/PROTECTED')
    pronet_dir = None
    for dir_name in os.listdir(base_dir):
        if dir_name.startswith(f'{prefix}{subject[:2]}'):
            pronet_dir = dir_name
            break
    zip_file_path = Path(base_dir, pronet_dir, 'raw', subject, 'mri')
    date_pattern = r'\d{4}_\d{1,2}_\d{1,2}'
    for filename in os.listdir(zip_file_path):
        date_match = re.search(date_pattern, filename)
        if date_match and entry_date != '':
            extracted_date = date_match.group(0)
            extracted_date = datetime.strptime(extracted_date, '%Y_%m_%d')
            print(extracted_date)
            print(formatted_entry_date)
            if not isinstance(formatted_entry_date, datetime):
                formatted_entry_date = datetime.strptime(formatted_entry_date,  '%Y_%m_%d')
            if formatted_entry_date == extracted_date and filename[-4:] == '.zip' and 'MR' in filename:
                zip_file = Path(base_dir, pronet_dir, 'raw', subject, 'mri',filename)
                if zip_file.exists():
                    print(zip_file)
                    stat = zip_file.stat()
                    timestamp = stat.st_mtime
                    date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                    return date_str
                else:
                    return ''
            else:
                continue



def date_of_qqc(subject, entry_date) -> str:
    mri_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    source_root = mri_root / 'sourcedata'
    date_numbers_only = re.sub('[-_]', '', entry_date)
    subject_dir = source_root / subject
    qqc_first_outputs = list(subject_dir.glob(f'*{date_numbers_only}*'))
    if qqc_first_outputs:
        qqc_first_output = qqc_first_outputs[0]
        ctime = qqc_first_output.stat().st_ctime
        date_str = datetime.fromtimestamp(ctime).strftime('%Y-%m-%d')
        return date_str
    else:
        return ''



def is_mri_done(subject, entry_date) -> bool:
    mri_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    deriv_root = mri_root / 'derivatives' / 'mriqc'

    date_numbers_only = re.sub('[-_]', '', entry_date)
    subject_dir = deriv_root / f'sub-{subject}'
    print(subject_dir)
    mriqc_first_outputs = subject_dir.glob(f'*{date_numbers_only}*')

    if len(list(mriqc_first_outputs)) >= 1:
        return True
    else:
        return False


def is_fmriprep_done(subject, entry_date) -> bool:
    mri_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    deriv_root = mri_root / 'derivatives' / 'fmriprep'

    date_numbers_only = re.sub('[-_]', '', entry_date)
    subject_dir = deriv_root / f'sub-{subject}'
    print(subject_dir)
    mriqc_first_outputs = subject_dir.glob(f'*{date_numbers_only}*')

    if len(list(mriqc_first_outputs)) >= 1:
        return True
    else:
        return False


def is_dwipreproc_done(subject, entry_date) -> bool:
    mri_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    deriv_root = mri_root / 'derivatives' / 'dwipreproc'

    date_numbers_only = re.sub('[-_]', '', entry_date)
    subject_dir = deriv_root / f'sub-{subject}'
    print(subject_dir)
    mriqc_first_outputs = subject_dir.glob(f'*{date_numbers_only}*')

    if len(list(mriqc_first_outputs)) >= 1:
        return True
    else:
        return False


def extract_variable_information(row: dict, col: str, variable_name: str,
                                 excluded_values: list, value_list: list) -> list:
    
    """This function takes a specific row and column from the given json file as input. Each 
    row is a dictionary and each column is a specific key in that dictionary.
    For a given subject's json file, there is a dictionary for each timepoint that
    contains the values for every variable within that timepoint. This function is used by the
    extract_missing_data_information function to loop through a given row (dictionary/timepoint) to
    search for the column (key/variable) that matches the variable name that it is searching for. It then 
    creates a string that contains the date from that row, the timepoint from that row, and
    the value for the specific variable that was being searched for."""
    
    domain_type_dict = {'1': 'clinical measures',
                        '2': 'EEG',
                        '3': 'Neuroimaging',
                        '4': 'cognition',
                        '5': 'genetic and fluid biomarkers',
                        '6': 'digital biomarkers',
                        '7': 'speech sampling'}

    reason_dict = {'M1': 'Refusal - no reason provided',
                   'M2': 'Refusal - reason: had an unpleasant experience last time',
                   'M3': 'Refusal - reason: anxiety associated with the assessment domain',
                   'M4': 'Refusal - reason: too much time commitment - AMP SCZ assessments',
                   'M5': 'Refusal - reason: too much time commitment - other studies',
                   'M6': 'No show',
                   'M7': 'Not booked',
                   'M8': 'Not applicable',
                   'M9': 'Uncontrollable circumstance',
                   'M10':  'Other reason'}

    value = row[col]
    date = row['chrmri_entry_date']

    if col == variable_name and row[col] not in excluded_values:
        if variable_name == 'missing_data_complete':
            if row[col] == '2':
                value = 'Complete'
            elif row[col] == '0':
                value = 'Incomplete'
        elif variable_name == 'chrmiss_domain':
            if row[col] == '1':
                value = 'Entire domain selected as missing'
        elif 'chrmiss_domain_type' in variable_name:
            #print(variable_name)
            for key, item in domain_type_dict.items():
                if key in col and row[col] == '1':
                    value = item
        elif 'chrmiss_domain_spec' in variable_name:
            for key, item in reason_dict.items():
                if key in row[col]:
                    value = item
        value_list.append(f"Timepoint: {row['redcap_event_name']} | "
                          f"Date: {date} | {value}")
    elif (variable_name == 'comment') and \
            (('mri' in col and 'comment' in col) and row[col] != '') or \
            (col == 'chrmri_missing' and row[col] != '') or \
            (col == 'chrmri_missing_spec' and row[col] != ''):
        if row[col] in row.values():
            if ('mri' in col and 'comment' in col and row[col] != ''):
                value_list.append(f"Timepoint: {row['redcap_event_name']} | "
                                  f"Date: {date} | {row[col]}")
    return value_list


def extract_missing_data_information(subject: str, network: str) -> list:
    
    """This function is given a specific subject and network as input. It then creates
    a path for the json file that is associated with that subject and network. For each variable
    that is being searched for in the json file, there is a list that will contain each value
    for that variable, along with its the date and timepoint."""
    
    
    if 'Pronet' in network:
        network = 'Pronet'
    else:
        network = 'Prescient'

    json_path = Path(f'/data/predict1/data_from_nda/{network}/PHOENIX/'
                     f'PROTECTED/{network}{subject[:2]}/raw/{subject}/'
                     f'surveys/{subject}.{network}.json')

    if json_path.exists():
        with open(json_path, 'r') as f:
            json_data = json.load(f)
    else:
        print(json_path)
        return ['Json not found', 'Json not found', 'Json not found',
                'Json not found', 'Json not found']

    comments_list = []
    missing_data_form_complete_list = []  # missing_data_complete
    domain_missing_list = []   # chrmiss_domain
    reason_for_missing_data_list = []   # chrmiss_domain_spec
    domain_type_missing_list = [] # chrmiss_domain_type
    variables = []

    for x in range(1, 8):
        variables.append('chrmiss_domain_type' + f'___{x}')
    variable_dict = {
            'variables': [
                {'missing_data_complete': ['']},
                {'chrmiss_domain': ['']},
                {'chrmiss_domain_spec': ['']}
                ]
            }
    for x in range(0, len(variables)):
        variable_dict['variables'].append({variables[x]: ['', '0']})
    value_lists = [missing_data_form_complete_list,
                   domain_missing_list,
                   reason_for_missing_data_list]
    for row in json_data:
        print(row['chric_record_id'])
        for col in row:
            comments_list = extract_variable_information(
                    row, col, 'comment', '', comments_list)
            for x in range(0, len(variable_dict['variables'])):
                for key, item in variable_dict['variables'][x].items():
                    if 'miss_domain_type' not in key:
                        value_lists[x] = extract_variable_information(
                                row, col, key, item, value_lists[x])
                    else:
                        domain_type_missing_list = \
                                extract_variable_information(
                                        row, col, key,
                                        item, domain_type_missing_list)
    list_of_lists = [domain_type_missing_list,
                     reason_for_missing_data_list,
                     domain_missing_list,
                     missing_data_form_complete_list,
                     comments_list]

    for x in range(0, len(list_of_lists)):
        list_of_lists[x] = list(set(list_of_lists[x]))
        list_of_lists[x] = re.sub(r'[\[\]]|\r?\n|\\N\\\\A|\n', '', str(list_of_lists[x]))
        list_of_lists[x] = re.sub(r'\s+', ' ', list_of_lists[x])

    return list_of_lists


def compare_dates(df: pd.DataFrame) -> pd.DataFrame:
    """This function is used to match the variables that were found 
    in the json files with the specific subject dates in the main
    pandas dataframe. If there are no variable dates that match the entry dates, the 
    variables are removed from the dataframe."""
    
    df['entry_date'] = df['entry_date'].str.replace('_', '-')

    for index, row in df.iterrows():
        entry_date = row['entry_date']
        print(entry_date)

        if pd.isna(entry_date):
            df.drop(index, inplace=True)
            continue

        for col in ['domain_type_missing', 'reason_for_missing_data',
                    'domain_missing', 'missing_data_form_complete',
                    'comments']:
            string_list = row[col].split(",'")
            for i in range(len(string_list)):
                string_list[i] = string_list[i].replace('"', '').replace(
                        "'", '')
                if string_list[i].count('|') >= 2:
                    date_str = string_list[i].split('|')[1].strip()[6:]
                    date_str = date_str.replace('_', '-')
                    if date_str == '' or entry_date == '':
                        string_list[i] = ''
                    else:
                        d1 = datetime.strptime(date_str, '%Y-%m-%d')
                        d2 = datetime.strptime(entry_date, '%Y-%m-%d')
                        if abs((d1 - d2).days) > 10:
                            string_list[i] = ''

            string_list = [s for s in string_list if s != '']
            row[col] = ','.join(string_list)
        df.loc[index] = row

    return df


def format_days(day_amount: int) -> str:
    '''Get 'day' or 'days' appended to the day_amount'''
    if isinstance(day_amount, float) and not math.isnan(day_amount):
        day_amount = int(day_amount)
        if day_amount == 1:
            day_amount = str(day_amount) + ' day'
        else:
            day_amount = str(day_amount) + ' days'

    return day_amount


def get_run_sheet_df(phoenix_dir: Path, datatype='mri') -> pd.DataFrame:
    run_sheets = grep_run_sheets(phoenix_dir)

    df = pd.DataFrame({'file_path': run_sheets})
    df['file_loc'] = df.file_path.apply(lambda x: str(x))
    df['subject'] = df.file_loc.str.extract('([A-Z]{2}\d{5})')
    df['datatype'] = df.file_path.apply(lambda x: x.name.split('_')[2])
    df['other_files'] = df['file_loc'].apply(lambda x: os.listdir(Path(x).parent.absolute()))
    df['other_files'] = df['other_files'].apply(lambda x: ', '.join(x))

    datatype_index = df[df['datatype'] == datatype].index
    datatype_df = df.loc[datatype_index]

    # check datatype file
    datatype_df['entry_date'] = datatype_df.file_path.apply(
            get_entry_date_from_run_sheet)

    # MRI
    datatype_df['mri_data_exist'] = datatype_df.apply(lambda x:
            check_mri_data(x['file_path'], x['entry_date']), axis=1)

    index_with_mri_data = datatype_df[
            datatype_df['mri_data_exist'] == True].index
    datatype_df.loc[index_with_mri_data, 'mri_arrival_date'] = \
            datatype_df.loc[index_with_mri_data].apply(lambda x:
                check_when_transferred(x['subject'], x['entry_date']), axis=1)
    missing_data_info = datatype_df.apply(
            lambda x: pd.Series(
                extract_missing_data_information(x['subject'],
                                                 str(phoenix_dir))), axis=1)
    datatype_df[['domain_type_missing', 'reason_for_missing_data',
                 'domain_missing', 'missing_data_form_complete',
                 'comments']] = missing_data_info.iloc[:, [0, 1, 2, 3, 4]]
    datatype_df = compare_dates(datatype_df)
    cols_to_split = ['domain_type_missing', 'reason_for_missing_data',
                     'domain_missing', 'missing_data_form_complete',
                     'comments']

    for x in range(0, len(cols_to_split)):
        mask = datatype_df[cols_to_split[x]].notnull() & \
                (datatype_df[cols_to_split[x]] != '')
        datatype_df.loc[mask, 'timepoint'] = datatype_df[mask][
                cols_to_split[x]].str.split('|').str[0].str.split(': ').str[1]

    for col in cols_to_split:
        datatype_df[col] = datatype_df[col].str.replace(
                r'^.*\|([^|]*$)', r'\1', regex=True)

    datatype_df['qqc_executed'] = datatype_df.apply(lambda x:
            is_qqc_executed(x['subject'], x['entry_date']), axis=1)

    datatype_df['mriqc_done'] = datatype_df.apply(lambda x:
            is_mri_done(x['subject'], x['entry_date']), axis=1)
    
    datatype_df['fmriprep_done'] = datatype_df.apply(lambda x:
            is_fmriprep_done(x['subject'], x['entry_date']), axis=1)

    datatype_df['dwipreproc_done'] = datatype_df.apply(lambda x:
            is_dwipreproc_done(x['subject'], x['entry_date']), axis=1)
    
    datatype_df['qqc_date'] = datatype_df.apply(lambda x:
            date_of_qqc(x['subject'], x['entry_date']), axis=1)
 
    datatype_df['zip_date'] = datatype_df.apply(
            lambda x, param: date_of_zip(x['subject'], x['entry_date'], param),
            axis=1, param=str(phoenix_dir))
    cols = datatype_df.columns.tolist()

    new_cols = ['subject', 'entry_date', 'timepoint'] + [
            col for col in cols if col not in
            ['subject', 'entry_date', 'timepoint', 'file_loc']]

    datatype_df = datatype_df[new_cols]
    datatype_df = datatype_df.reset_index()
    datatype_df['qqc_date'] = pd.to_datetime(datatype_df['qqc_date'])
    datatype_df['zip_date'] = pd.to_datetime(datatype_df['zip_date'])
    datatype_df['entry_date'] = pd.to_datetime(datatype_df['entry_date'])

    # estimate time difference
    arrival_qqc_time = lambda x: abs((x['zip_date'] - x['qqc_date']).days)
    arrival_scan_time = lambda x: abs((x['zip_date'] - x['entry_date']).days)
    datatype_df['Time between QQC and data arrival'] = datatype_df.apply(
            arrival_qqc_time, axis=1).apply(format_days)
    datatype_df['Time between scan and data arrival'] = datatype_df.apply(
            arrival_scan_time, axis=1).apply(format_days)
    datatype_df.reset_index(drop=True,inplace=True)
    datatype_df['index'] = ''

    return datatype_df
