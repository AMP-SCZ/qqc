from ampscz_asana.lib.server_scanner import grep_run_sheets
import re
import pandas as pd
from pathlib import Path
from ampscz_asana.lib.utils import convert_AU_to_US_date
from datetime import datetime
import os
import math
import json
from typing import Union

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


def get_mri_data(run_sheet: Path, entry_date: str) -> bool:
    ''''return the matching MRI zip file based on the entry_date

    Key argument:
        run_sheet: Path of the run sheet file used to get MRI folder, Path
        entry_date: date in YYYY_MM_DD format, str.

    Notes:
        The function will work regardless of zero padding in month and day of
        the entry_date, eg) 2000_03_03, 2000_3_3, 2000_03_3, and 2000_3_03
        will all be matched to 2022_03_03 pattern in the file name.
    '''
    if entry_date == '':
        return None

    # exact match
    for zip_file in run_sheet.parent.glob(f'*{entry_date}*.[Zz][Ii][Pp]'):
        return zip_file

    # date match
    for zip_file in run_sheet.parent.glob('*.[Zz][Ii][Pp]'):
        zip_filename_pattern = r'[A-Z]{2}\d{5}_MR_(\d{4}_\d{1,2}_\d{1,2})_'
        matching_pattern = re.search(zip_filename_pattern, zip_file.name)
        if matching_pattern:
            date_from_filename_str = matching_pattern.group(1)
            date_from_filename_date = datetime.strptime(date_from_filename_str,
                                                        '%Y_%m_%d')
            entry_date_date = datetime.strptime(entry_date, '%Y_%m_%d')

            if date_from_filename_date == entry_date_date:
                return zip_file

    return None


def check_mri_data(run_sheet: Path, entry_date: str) -> bool:
    ''''return if there is MR data and entry date

    Key argument:
        run_sheet: Path of the run sheet file, Path
        entry_date: date in YYYY_MM_DD format, str.


    Notes:
        The function will work regardless of zero padding in month and day of
        the entry_date, eg) 2000_03_03, 2000_3_3, 2000_03_3, and 2000_3_03
        will all be matched to 2022_03_03 pattern in the file name.
    '''
    if entry_date == '':
        return False

    # exact match
    for zip_file in run_sheet.parent.glob(f'*{entry_date}*.[Zz][Ii][Pp]'):
        return True

    # date match
    for zip_file in run_sheet.parent.glob('*.[Zz][Ii][Pp]'):
        zip_filename_pattern = r'[A-Z]{2}\d{5}_MR_(\d{4}_\d{1,2}_\d{1,2})_'
        matching_pattern = re.search(zip_filename_pattern, zip_file.name)
        if matching_pattern:
            date_from_filename_str = matching_pattern.group(1)
            date_from_filename_date = datetime.strptime(date_from_filename_str,
                                                        '%Y_%m_%d')
            entry_date_date = datetime.strptime(entry_date, '%Y_%m_%d')

            if date_from_filename_date == entry_date_date:
                return True

    return False


def check_when_transferred(expected_mri_path: Union[Path, str]) -> bool:
    ''''return the ctime of a file'''
    ctime = Path(expected_mri_path).stat().st_ctime
    date_str = datetime.fromtimestamp(ctime).strftime('%Y-%m-%d')
    return date_str


def is_qqc_executed(subject, entry_date) -> bool:
    if entry_date == '' or pd.isna(entry_date):
        return False

    mri_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    source_root = mri_root / 'sourcedata'

    date_numbers_only = re.sub('[-_]', '', entry_date)
    subject_dir = source_root / subject
    qqc_first_outputs = subject_dir.glob(f'*{date_numbers_only}*')

    if len(list(qqc_first_outputs)) >= 1:
        return True
    else:
        return False


def date_of_zip(subject, entry_date, phoenix_dir):
    if entry_date == '' or pd.isna(entry_date):
        return None
    formatted_entry_date = entry_date.replace("-", "_")
    formatted_entry_date = datetime.strptime(formatted_entry_date, '%Y_%m_%d')
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
            if formatted_entry_date == extracted_date and \
                    filename[-4:] == '.zip' and 'MR' in filename:
                zip_file = zip_file_path / filename
                stat = zip_file.stat()
                timestamp = stat.st_mtime
                date_str = datetime.fromtimestamp(timestamp).strftime(
                        '%Y-%m-%d')
                return date_str
            else:
                continue


def date_of_qqc(subject, entry_date) -> str:
    if entry_date == '' or pd.isna(entry_date):
        return ''

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
    if entry_date == '' or pd.isna(entry_date):
        return False
    mri_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    deriv_root = mri_root / 'derivatives' / 'mriqc'

    date_numbers_only = re.sub('[-_]', '', entry_date)
    subject_dir = deriv_root / f'sub-{subject}'
    mriqc_first_outputs = subject_dir.glob(f'*{date_numbers_only}*')

    if len(list(mriqc_first_outputs)) >= 1:
        return True
    else:
        return False


def is_fmriprep_done(subject, entry_date) -> bool:
    if entry_date == '' or pd.isna(entry_date):
        return False
    mri_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    deriv_root = mri_root / 'derivatives' / 'fmriprep'

    date_numbers_only = re.sub('[-_]', '', entry_date)
    subject_dir = deriv_root / f'sub-{subject}'
    mriqc_first_outputs = subject_dir.glob(f'*{date_numbers_only}*')

    if len(list(mriqc_first_outputs)) >= 1:
        return True
    else:
        return False


def is_dwipreproc_done(subject, entry_date) -> bool:
    if entry_date == '' or pd.isna(entry_date):
        return False
    mri_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    deriv_root = mri_root / 'derivatives' / 'dwipreproc'

    date_numbers_only = re.sub('[-_]', '', entry_date)
    subject_dir = deriv_root / f'sub-{subject}'
    mriqc_first_outputs = subject_dir.glob(f'*{date_numbers_only}*')

    if len(list(mriqc_first_outputs)) >= 1:
        return True
    else:
        return False


def extract_variable_information(row: dict, col: str,
                                 variable_name: str, excluded_values: list,
                                 value_list: list) -> list:
    """Extract info from the 'row' dictionary, which is from REDCap json.

    This function takes a specific row and column from the given json file as
    input. Each row is a dictionary and each column is a specific key in that
    dictionary. For a given subject's json file, there is a dictionary for
    each timepoint that contains the values for every variable within that
    timepoint. This function is used by the extract_missing_data_information
    function to loop through a given row (dictionary/timepoint) to search for
    the column (key/variable) that matches the variable name that it is
    searching for. It then creates a string that contains the date from that
    row, the timepoint from that row, and the value for the specific variable
    that was being searched for.

    Key Arguments:
        row: data from REDCap json, dict.
        col: key of the dictionary, str.
        variable_name: variable name, str.
        excluded_values: list of excluded values, list of str.
        value_list: list of values, list of str.
    """

    domain_type_dict = {'1': 'clinical measures',
                        '2': 'EEG',
                        '3': 'Neuroimaging',
                        '4': 'cognition',
                        '5': 'genetic and fluid biomarkers',
                        '6': 'digital biomarkers',
                        '7': 'speech sampling'}

    reason_dict = {
        'M1': 'Refusal - no reason provided',
        'M2': 'Refusal - reason: had an unpleasant experience last time',
        'M3': 'Refusal - reason: anxiety associated with the '
              'assessment domain',
        'M4': 'Refusal - reason: too much time commitment '
              '- AMP SCZ assessments',
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


def extract_missing_data_information(subject: str, phoenix_dir: str) -> list:
    """This function is given a specific subject and network as input. It then creates
    a path for the json file that is associated with that subject and network. For each variable
    that is being searched for in the json file, there is a list that will contain each value
    for that variable, along with its the date and timepoint."""
    
    if 'Pronet' in str(phoenix_dir):
        network = 'Pronet'
    else:
        network = 'Prescient'

    site = network + subject[:2]
    subject_dir = Path(phoenix_dir) / f'PROTECTED/{site}/raw/{subject}'
    json_path = subject_dir / 'surveys' / f'{subject}.{network}.json'

    if json_path.exists():
        with open(json_path, 'r') as f:
            json_data = json.load(f)
    else:
        return ['Json not found', 'Json not found', 'Json not found',
                'Json not found', 'Json not found']

    comments_list = []
    missing_data_form_complete_list = []  # missing_data_complete
    domain_missing_list = []  # chrmiss_domain
    reason_for_missing_data_list = []  # chrmiss_domain_spec
    domain_type_missing_list = []  # chrmiss_domain_type
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


def extract_mri_comments(run_sheet: Path) -> str:
    '''Extract comments from MRI run sheet'''

    if 'Prescient' in str(run_sheet):
        df = pd.read_csv(run_sheet).T.reset_index()
        df.columns = ['field_name', 'field_value']
    else:
        df = pd.read_csv(run_sheet)

    comment_df = df[df['field_name'].str.contains('_comment')]
    comment_df = comment_df[~comment_df['field_value'].isnull()]
    comment_df = comment_df[comment_df['field_value'] != -3]

    text = ''
    for comment, table in comment_df.groupby('field_value'):
        text += f'{comment} :'
        text += ', '.join(table['field_name'].to_list()) + '\n'

    return text


def extract_session_num(run_sheet: Path) -> str:
    '''Extract session number from MRI run sheet'''

    if 'Prescient' in str(run_sheet):
        df = pd.read_csv(run_sheet).T.reset_index()
        df.columns = ['field_name', 'field_value']
    else:
        df = pd.read_csv(run_sheet)

    session_index = df[df['field_name'] == 'chrmri_session_num'].index
    session_str = df.loc[session_index]['field_value']

    return session_str
    try:
        int(session_str)
    except ValueError:
        return None


def extract_missing_data_info_new(subject: str,
                                  phoenix_dir: str,
                                  scan_date: str,
                                  timepoint: Union['1', '2']) -> tuple:
    '''Extract missing info and timepoint from REDCap'''
    if 'Pronet' in str(phoenix_dir):
        network = 'Pronet'
    else:
        network = 'Prescient'

    site = network + subject[:2]
    subject_dir = Path(phoenix_dir) / f'PROTECTED/{site}/raw/{subject}'
    json_path = subject_dir / 'surveys' / f'{subject}.{network}.json'

    if json_path.exists():
        with open(json_path, 'r') as f:
            json_data = json.load(f)
    else:
        return None

    # load json file into json
    df = pd.DataFrame(json_data)

    # column names to extract
    domain_type_cols = [x for x in df.columns
                        if re.search(r'chrmiss_domain_type___3', x)]
    miss_time_cols = [x for x in df.columns if 'chrmiss_time' == x]

    if len(domain_type_cols) == 0 and len(miss_time_cols) == 0:
        return None

    # select columns in interest
    df = df[['redcap_event_name',
             'chrmri_entry_date',
             'chrmiss_domain_spec'] + domain_type_cols + miss_time_cols]

    if scan_date == '' or pd.isna(scan_date):
        timepoint_to_index_dict = {'1': 'baseline',
                                   '2': 'month_2'}
        timepoint_str = timepoint_to_index_dict[timepoint]
        try:
            scan_date_index = df[
                    df.redcap_event_name.str.contains(timepoint_str)].index[0]
        except IndexError:
            return None
    else:
        # only leave the event where there is matching chrmri_entry_date
        scan_date = datetime.strptime(scan_date,
                                      '%Y_%m_%d').strftime('%Y-%m-%d')

        # [0] added at the end because it returns list of a singe item
        try:
            scan_date_index = df[df.chrmri_entry_date == scan_date].index[0]
        except IndexError:
            return None

    timepoint = df.loc[scan_date_index]['redcap_event_name']
    missing_info = df.loc[scan_date_index]['chrmiss_domain_type___3']

    if 'chrmiss_time' in df.columns:
        miss_time = df.loc[scan_date_index]['chrmiss_time']
    else:
        miss_time = None

    return (missing_info, timepoint, miss_time)


def compare_dates(df: pd.DataFrame) -> pd.DataFrame:
    """This function is used to match the variables that were found 
    in the json files with the specific subject dates in the main
    pandas dataframe. If there are no variable dates that match the entry
    dates, the variables are removed from the dataframe."""

    df['entry_date'] = df['entry_date'].str.replace('_', '-')

    for index, row in df.iterrows():
        entry_date = row['entry_date']

        # if pd.isna(entry_date):
            # df.drop(index, inplace=True)
            # continue

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


def get_run_sheet_df(phoenix_dir: Path,
                     datatype: str = 'mri',
                     test: bool = False) -> pd.DataFrame:
    '''Summarize the raw data files based on the lochness created run sheets

    Key Arguments:
        phoenix_dir: Root of a PHOENIX directory, Path.
        datatype: data type, eg) 'mri', str.
    '''
    # get all run sheets extracted from RPMS or REDCap by lochness from
    run_sheets = grep_run_sheets(phoenix_dir)

    # if test:
        # run_sheets = run_sheets[:5]

    # create dataframe
    df = pd.DataFrame({'file_path': run_sheets})
    df['file_loc'] = df.file_path.apply(lambda x: str(x))
    # add network
    df['network'] = df.file_loc.str.contains('Prescient').map(
            {True: 'Prescient',
             False: 'Pronet'})

    # YA08362.Pronet.Run_sheet_mri_2.csv
    df['run_sheet_num'] = df.file_path.apply(lambda x: x.name).str.extract(
            '[A-Z]{2}\d{5}\.P\w+\.Run_sheet_\w+_(\d).csv')
    df['subject'] = df.file_loc.str.extract('([A-Z]{2}\d{5})')
    # AB00001.Pronet.Run_sheet_mri_1.csv
    df['datatype'] = df.file_path.apply(lambda x: x.name.split('_')[2])
    df['other_files'] = df['file_loc'].apply(lambda x: [x for x in os.listdir(
        Path(x).parent.absolute()) if re.search(r'zip', x, re.IGNORECASE)])
    df['other_files'] = df['other_files'].apply(lambda x: ', '.join(x))

    # select given datatype
    datatype_index = df[df['datatype'] == datatype].index
    datatype_df = df.loc[datatype_index]

    # check datatype file
    datatype_df['entry_date'] = datatype_df.file_path.apply(
            get_entry_date_from_run_sheet)

    # extract comments from run sheet
    datatype_df['run_sheet_comment'] = datatype_df.file_path.apply(
            extract_mri_comments)

    # extract comments from run sheet
    datatype_df['session_num'] = datatype_df.file_path.apply(
            extract_session_num)

    # for each run sheet, return the matching zip file
    datatype_df['expected_mri_path'] = datatype_df.apply(lambda x:
            get_mri_data(x['file_path'], x['entry_date']), axis=1)

    datatype_df['mri_data_exist'] = datatype_df.apply(lambda x:
            check_mri_data(x['file_path'], x['entry_date']), axis=1)

    # index of run sheets with matching MRI file
    index_with_mri_data = datatype_df[
            datatype_df['mri_data_exist'] == True].index

    # estimate MRI zip file arrival date
    datatype_df.loc[index_with_mri_data, 'mri_arrival_date'] = \
            datatype_df.loc[index_with_mri_data].expected_mri_path.apply(
                check_when_transferred)

    # extract missing data information and timepoint from the full REDCap data
    datatype_df['vars'] = datatype_df.apply(
            lambda x: extract_missing_data_info_new(x['subject'],
                                                    phoenix_dir,
                                                    x['entry_date'],
                                                    x['run_sheet_num']),
            axis=1)

    datatype_df['missing_info'] = datatype_df.vars.str[0]
    datatype_df['timepoint'] = datatype_df.vars.str[1]
    datatype_df['missing_timepoint'] = datatype_df.vars.str[2]
    datatype_df['missing_marked'] = (
            (datatype_df['missing_info'] == 1) |
            (datatype_df['missing_timepoint'])).map({True: 1, False: None})
    datatype_df.drop('vars', axis=1, inplace=True)

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
    datatype_df['entry_date'] = datatype_df['entry_date'].str.replace('_', '-')

    datatype_df = datatype_df.reset_index()
    datatype_df['qqc_date'] = pd.to_datetime(datatype_df['qqc_date'])
    datatype_df['zip_date'] = pd.to_datetime(datatype_df['zip_date'],
                                             errors='ignore')
    datatype_df['entry_date'] = pd.to_datetime(datatype_df['entry_date'])

    # estimate time difference
    arrival_qqc_time = lambda x: abs((x['zip_date'] - x['qqc_date']).days)
    arrival_scan_time = lambda x: abs((x['zip_date'] - x['entry_date']).days)
    delay_time = lambda x: abs((datetime.today() - x['entry_date']).days)
    datatype_df['days_arrival_to_qqc'] = datatype_df.apply(arrival_qqc_time,
                                                           axis=1)
    datatype_df['days_scan_to_arrival'] = datatype_df.apply(arrival_scan_time,
                                                            axis=1)
    datatype_df['days_scan_to_today'] = datatype_df.apply(delay_time, axis=1)
    datatype_df.reset_index(drop=True,inplace=True)
    datatype_df.drop('index', axis=1, inplace=True)


    return datatype_df


def dataflow_dpdash(datatype_df: pd.DataFrame,
                    outdir: Path,
                    test: bool = False) -> None:
    '''Convert datatype_df to DPDash importable format and save as csv files'''
    # flush existing files
    if not test:
        for i in outdir.glob('*mridataflow-day*csv'):
            os.remove(i)

    # loop through each subject to build database
    all_df = pd.DataFrame()
    for subject, table in datatype_df.groupby('subject'):
        for num, (timepoint, t_table) in enumerate(
                table.sort_values('timepoint').groupby('run_sheet_num'), 1):
            row = t_table.iloc[0]

            df_tmp = pd.DataFrame({
                'day': [num],
                'reftime': '',
                'timeofday': '',
                'weekday': '',
                'subject_id': subject,
                'site': subject[:2],
                'network': row['network'],
                'timepoint': row['run_sheet_num'],
                'scan_date': row['entry_date'],
                'missing_info': row['missing_info'],
                'quick_qc': int(row['qqc_executed']),
                'manual_qc': 3,
                'data_at_dpacc': int(row['mri_data_exist']),
                'days_arrival_to_qqc': row['days_arrival_to_qqc'],
                'days_scan_to_arrival': row['days_scan_to_arrival'],
                'days_scan_to_today': row['days_scan_to_today']})

            all_df = pd.concat([all_df, df_tmp])

    all_df['scan_date_missing'] = all_df.scan_date.apply(lambda x: 1 if
            pd.isna(x) else 0)
    all_df['scan_date'] = all_df.scan_date.fillna('No Scan Date')

    if test:
        return all_df

    # save CSV files
    # combined
    filename = f'combined-AMPSCZ-mridataflow-day1to{len(all_df)}.csv'
    nodate_df = all_df[all_df.scan_date.isnull()]
    date_df = all_df[~all_df.scan_date.isnull()]
    date_df.sort_values(['data_at_dpacc', 'days_scan_to_today', 'scan_date'],
                        inplace=True)
    all_df = pd.concat([date_df, nodate_df])
    all_df['day'] = range(1, len(all_df)+1)
    all_df.to_csv(outdir / filename, index=False)

    # for each network
    for network, table in all_df.groupby('network'):
        filename = f'combined-{network.upper()}-' \
                   f'mridataflow-day1to{len(table)}.csv'
        table['day'] = range(1, len(table)+1)
        table.to_csv(outdir / filename, index=False)

    # for each site
    for site, table in all_df.groupby('site'):
        filename = f'combined-{site}-mridataflow-day1to{len(table)}.csv'
        table['day'] = range(1, len(table)+1)
        table.to_csv(outdir / filename, index=False)

    # for each subject
    for subject, table in all_df.groupby('subject_id'):
        site = subject[:2]
        filename = f'{site}-{subject}-mridataflow-day1to{len(table)}.csv'
        table['day'] = range(1, len(table)+1)
        table.to_csv(outdir / filename, index=False)
