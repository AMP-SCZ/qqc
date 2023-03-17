from pathlib import Path
import os
import sys
import shutil
import string
from random import choice, randint
from datetime import datetime, timedelta
import pandas as pd
import json
import pytest

TEST_LIB_PATH = Path(__file__).parent
TEST_ROOT_PATH = TEST_LIB_PATH.parent
ASANA_ROOT = TEST_ROOT_PATH.parent
sys.path.append(str(ASANA_ROOT))

from ampscz_asana.server_scanner import grep_subject_files, \
        send_to_caselist, consent_date_extraction, \
        consent_date_extraction_csv
from ampscz_asana.qc import get_run_sheet_df
from ampscz_asana.asana_api import get_all_task, get_all_subtask, \
        get_task_with_str, get_subtask_with_str, \
        get_asana_ready, create_new_task, \
        get_all_sections, get_section_with_str, \
        create_new_eeg_subtask, create_new_subtask
from ampscz_asana.utils import add_days_to_str_date


def return_json_loc_pronet(ampscz_id: str) -> Path:
    '''Return pronet json loch'''
    phoenix_fake = TEST_LIB_PATH / 'test_PHOENIX'
    site = ampscz_id[:2]
    subject_raw_path = phoenix_fake / 'PROTECTED' / ('Pronet' + site) / \
            'raw' / ampscz_id
    fake_json = subject_raw_path / 'surveys' / f'{ampscz_id}.Pronet.json'

    return fake_json


def return_csv_loc_prescient(ampscz_id: str) -> Path:
    '''Return prescient csv loch'''
    phoenix_fake = TEST_LIB_PATH / 'test_PHOENIX'
    site = ampscz_id[:2]
    subject_raw_path = phoenix_fake / 'PROTECTED' / ('Prescient' + site) / \
            'raw' / ampscz_id
    fake_csv = subject_raw_path / 'surveys' / \
            f'{ampscz_id}_informed_consent_run_sheet.csv'

    return fake_csv


def create_subject(ampscz_id: str, network: str, mode=1) -> Path:
    '''Create fake PRONET json'''

    if network == 'pronet':
        fake_json_loc = return_json_loc_pronet(ampscz_id)
        fake_json_loc.parent.mkdir(exist_ok=True, parents=True)
        if mode == 1:
            fake_dict_list = [
                {"chric_ampscz_id": ampscz_id,
                 "chric_consent_date": datetime.today().strftime('%Y-%m-%d')}
                    ]
        elif mode == 2:
            return fake_json_loc

        with open(fake_json_loc, 'w') as fp:
            json.dump(fake_dict_list, fp)

    else:
        fake_json_loc = return_csv_loc_prescient(ampscz_id)
        fake_json_loc.parent.mkdir(exist_ok=True, parents=True)
        if mode == 1:
            df = pd.DataFrame({
                'subjectkey': [ampscz_id],
                'LastModifiedDate': \
                        datetime.now().strftime('%d/%m/%Y %I:%M:%S %p'),
                'interview_date': (datetime.now() - 
                    timedelta(days=1)).strftime('%d/%m/%Y %I:%M:%S %p'),
                'interview_age': 20,
                'gender': choice([1, 2]),
                'visit': 1,
                'version': '',
                'group': choice(['UHR', 'HC']),
                'chric_consent_date': (
                    datetime.now() - timedelta(days=1)).strftime(
                        '%d/%m/%Y %I:%M:%S %p')
                })
        elif mode == 2:
            return fake_json_loc

        df.to_csv(fake_json_loc, index=False)

    return fake_json_loc


def get_random_ampscz_id() -> str:
    first_letter = choice(string.ascii_uppercase)
    second_letter = choice(string.ascii_uppercase)
    random_digits = str(randint(0, 99999)).zfill(5)
    subject = first_letter + second_letter + random_digits

    return subject


def run_tree():
    print(os.popen(f'tree {TEST_LIB_PATH}/test_PHOENIX').read())


class FakeSubject:
    def __init__(self, network):
        subject_id = get_random_ampscz_id()
        self.subject_id = subject_id
        if network == 'pronet':
            fake_json_loc = create_subject(subject_id, network='pronet')
        else:
            fake_json_loc = create_subject(subject_id, network='prescient')
        self.phoenix_root = Path('test_PHOENIX')


@pytest.fixture
def get_pronet_fake_subject():
    return FakeSubject('pronet')


@pytest.fixture
def get_prescient_fake_subject():
    return FakeSubject('prescient')


def test_create_new_task(get_pronet_fake_subject):
    ampscz_id = get_pronet_fake_subject.subject_id
    phoenix_root = get_pronet_fake_subject.phoenix_root
    client, workspace_gid, project_gid = get_asana_ready()

    # if pronet
    consent_date = consent_date_extraction(ampscz_id,
                                           phoenix_root)
    subject_info_dict = {}
    subject_info_dict['consent_date'] = consent_date
    subject_info_dict['end_date'] = (datetime.strptime(
            consent_date, '%Y-%m-%d') + timedelta(days=1)
            ).strftime('%Y-%m-%d')
    create_new_task(client,
                    ampscz_id, subject_info_dict,
                    workspace_gid, project_gid)


def test_create_new_eeg_subtask(get_pronet_fake_subject):
    ampscz_id = get_pronet_fake_subject.subject_id
    phoenix_root = get_pronet_fake_subject.phoenix_root
    client, workspace_gid, project_gid = get_asana_ready()

    # if pronet
    consent_date = consent_date_extraction(ampscz_id,
                                           phoenix_root)
    subject_info_dict = {}
    subject_info_dict['consent_date'] = consent_date
    subject_info_dict['end_date'] = (datetime.strptime(
            consent_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    create_new_task(client,
                    ampscz_id, subject_info_dict,
                    workspace_gid, project_gid)

    # if pronet
    create_new_eeg_subtask(client,
                           ampscz_id,
                           workspace_gid,
                           project_gid,
                           '2022-09-22',
                           '2022-09-23')

def test_delete_task():
    client, workspace_gid, project_gid = get_asana_ready('AMP-SCZ MRI dataflow & QC')
    tasks = client.tasks.get_tasks_for_project(project_gid)
    for task in tasks:
        print(task)
        client.tasks.delete_task(task['gid'])


def test_mri_pipeline():
    import pandas as pd
    import re

    phoenix_dir = Path('/data/predict/data_from_nda/Pronet/PHOENIX')
    client, workspace_gid, project_gid = get_asana_ready(
            project_name = 'AMP-SCZ MRI dataflow & QC')
    df = pd.concat([get_run_sheet_df(phoenix_dir),
                    get_run_sheet_df(phoenix_dir)])

    tasks = get_all_task(client, project_gid)
    today_date_string = datetime.today().strftime('%Y-%m-%d')
    tomorrow_date_string = (
            timedelta(days=1) + datetime.today()
            ).strftime('%Y-%m-%d')

    for _, row in df.iterrows():
        entry_date_numbers_only = re.sub('_', '-', row.entry_date)
        if entry_date_numbers_only == '':
            print('\nNo proper entry date on REDCap run sheet')
            print(row.subject)
            print(row.entry_date)
            print('\nList of files')
            for i in row.file_path.parent.glob('*'):
                print(f'\t\tt{i.name}')
            continue

        print(f'Going through subject {row.subject} {row.entry_date}')
        task = get_task_with_str(tasks, row.subject)
        if task is None:
            print('\tNew subject')
            task = client.tasks.create_in_workspace(workspace_gid,
                {'name': row.subject,
                 'note': 'New Data has been uploaded for ' + row.subject,
                 'assignee': 'kevincho@bwh.harvard.edu',
                 'projects': [project_gid],
                 'start_on': entry_date_numbers_only,
                 'due_on': add_days_to_str_date(entry_date_numbers_only, 7)})

        subtasks = get_all_subtask(client, task)
        # if run sheet exists, but no MRI data
        print(f'\tChecking if {row.subject} have MRI data')
        if not row.mri_data_exist:
            subtask_name = 'Run sheet exists but no MRI yet'
            subtask = get_subtask_with_str(subtasks, subtask_name)
            section_name = 'Run sheet scan date'
            if subtask is None:  # if doesn't exist
                create_new_subtask(
                    client, row.subject, workspace_gid, project_gid,
                    subtask_name,
                    section_name,
                    entry_date_numbers_only,
                    tomorrow_date_string,
                    phoenix_dir)
            else:  # if it exist, update the 'due_on'
                client.tasks.update_task(
                        subtask['gid'],
                        {'due_on': tomorrow_date_string})
        else:
            # if there is now MRI data, complete the task
            subtask_name = 'Run sheet exists but no MRI yet'
            subtask = get_subtask_with_str(subtasks, subtask_name)
            if subtask is not None:
                print(f'\tNow there is data for {row.subject}')
                print(subtask)
                if not subtask['completed']:
                    client.tasks.update_task(subtask['gid'],
                                             {'completed': True})

            # 'Manual QC',
            subtask_name = 'Manual QC'
            subtask = get_subtask_with_str(subtasks, subtask_name)
            section_name = 'Manual QC'
            if subtask is None:
                create_new_subtask(
                    client, row.subject, workspace_gid, project_gid,
                    subtask_name,
                    section_name,
                    entry_date_numbers_only,
                    add_days_to_str_date(entry_date_numbers_only, 3),
                    phoenix_dir)

            subtask_names = ['QQC', 'fMRIPrep',
                             'MRIQC', 'DWI preprocessing']
            table_columns = ['qqc_executed', 'fmriprep_done',
                            'mriqc_done', 'dwipreproc_done']
            for subtask_name, col in zip(subtask_names, table_columns):
                print(f'\tChecking if {row.subject} have {subtask_name} '
                      'subtask')
                # get matching subtask
                subtask = get_subtask_with_str(subtasks, subtask_name)
                section_name = 'Automatic QC'

                if not row[col]:  # if not done
                    if subtask is None:  # create subtask if doesn't exist
                        create_new_subtask(
                            client, row.subject, workspace_gid, project_gid,
                            subtask_name,
                            section_name,
                            entry_date_numbers_only,
                            add_days_to_str_date(entry_date_numbers_only, 3),
                            phoenix_dir)
                    else:
                        client.tasks.update_task(subtask['gid'],
                                                 {'completed': False})

                else:  # if done
                    if subtask is not None:
                        if 'completed' in subtask:
                            if not subtask['completed']:
                                client.tasks.update_task(subtask['gid'],
                                                         {'completed': True})
                        else:
                            client.tasks.update_task(subtask['gid'],
                                                     {'completed': True})


