from ampscz_asana.lib.server_scanner import grep_run_sheets
import re
import pandas as pd
from pathlib import Path
from ampscz_asana.lib.utils import convert_AU_to_US_date
from datetime import datetime
import os

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

phoenix_dir = Path('/data/predict/data_from_nda/Pronet/PHOENIX')
phoenix_dir = Path('/data/predict/data_from_nda/Prescient/PHOENIX')


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
    mri_root = Path('/data/predict/data_from_nda/MRI_ROOT')
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
    mri_root = Path('/data/predict/data_from_nda/MRI_ROOT')
    source_root = mri_root / 'sourcedata'

    date_numbers_only = re.sub('[-_]', '', entry_date)
    print(date_numbers_only)
    subject_dir = source_root / subject
    qqc_first_outputs = subject_dir.glob(f'*{date_numbers_only}*')

    if len(list(qqc_first_outputs)) >= 1:
        return True
    else:
        return False

    
    
def date_of_zip(subject, entry_date):
    base_dir = Path(f'/data/predict1/data_from_nda/Pronet/PHOENIX/PROTECTED')
    prefix = subject[:2]
    pronet_dir = None
    for dir_name in os.listdir(base_dir):
        if dir_name.startswith(f'Pronet{prefix}'):
            pronet_dir = dir_name
            break
    zip_file = Path(base_dir, pronet_dir, 'raw', subject, 'mri', f'{subject}_MR_{entry_date}_1.zip')
    if zip_file.exists():
        stat = zip_file.stat()
        timestamp = stat.st_mtime
        date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        return date_str     
    else:
        return ''

def date_of_qqc(subject, entry_date) -> str:
    mri_root = Path('/data/predict/data_from_nda/MRI_ROOT')
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
    mri_root = Path('/data/predict/data_from_nda/MRI_ROOT')
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
    mri_root = Path('/data/predict/data_from_nda/MRI_ROOT')
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
    mri_root = Path('/data/predict/data_from_nda/MRI_ROOT')
    deriv_root = mri_root / 'derivatives' / 'dwipreproc'

    date_numbers_only = re.sub('[-_]', '', entry_date)
    subject_dir = deriv_root / f'sub-{subject}'
    print(subject_dir)
    mriqc_first_outputs = subject_dir.glob(f'*{date_numbers_only}*')

    if len(list(mriqc_first_outputs)) >= 1:
        return True
    else:
        return False

def get_run_sheet_df(phoenix_dir: Path, datatype='mri') -> pd.DataFrame:
    run_sheets = grep_run_sheets(phoenix_dir)

    df = pd.DataFrame({'file_path': run_sheets})
    df['file_loc'] = df.file_path.apply(lambda x: str(x))
    df['subject'] = df.file_loc.str.extract('([A-Z]{2}\d{5})')
    df['datatype'] = df.file_path.apply(lambda x: x.name.split('_')[2])
    df['other_files'] = df['file_loc'].apply(lambda x: os.listdir(Path(x).parent.absolute()))

    


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
    
    datatype_df['zip_date'] = datatype_df.apply(lambda x:
            date_of_zip(x['subject'], x['entry_date']), axis=1)
    
    return datatype_df

    # for _, i in datatype_df[~datatype_df.check_data].iterrows():
        # print(i.subject)
        # print(f'Entry date on the run sheet: {i.entry_date}')
        # for j in i.file_path.parent.glob('*'):
            # print(j)

        # print('-'*80)

