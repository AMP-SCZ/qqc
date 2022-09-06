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

from lib.server_scanner import grep_all_paths, grep_subject_files, \
        grep_id_basename, send_to_caselist


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
                {"chric_ampscz_id": ampscz_id},
                {"chric_consent_date": datetime.today().strftime('%Y-%m-%d')}
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
        if network == 'pronet':
            fake_json_loc = create_subject(subject_id, network='pronet')
        else:
            fake_json_loc = create_subject(subject_id, network='prescient')


@pytest.fixture
def get_pronet_fake_subject():
    return FakeSubject('pronet')


@pytest.fixture
def get_prescient_fake_subject():
    return FakeSubject('prescient')


def test_fixtures(get_pronet_fake_subject, get_prescient_fake_subject):
    pass
