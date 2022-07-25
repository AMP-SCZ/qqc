import pytest
import pandas as pd
from pathlib import Path
import qqc
import os
import pydicom
from typing import Union
import time
import numpy as np
import shutil
import re
import json

from qqc import json_check_for_a_session, json_check

pd.set_option('max_columns', 10)


def test_json_check_for_a_session():
    data_root = '/data/predict/phantom_data/kcho/devel_soft/qqc/tests/scripts/testroot/sub-testsubject/ses-testsession/dwi'
    json_files = [ 
        'sub-testsubject_ses-testsession_acq-176_dir-PA_dwi.json',
        'sub-testsubject_ses-testsession_acq-176_dir-PA_sbref.json'
        ]
    json_files = [Path(data_root) / x for x in json_files]
    json_check_for_a_session(json_files, True, True, specific_field='ShimSetting')


def test_json_check_only():
    data_root = '/data/predict/phantom_data/kcho/devel_soft/qqc/tests/scripts/testroot/sub-testsubject/ses-testsession/dwi'
    json_files = [ 
        'sub-testsubject_ses-testsession_acq-176_dir-PA_dwi.json',
        'sub-testsubject_ses-testsession_acq-176_dir-PA_sbref.json'
        ]
    json_files = [Path(data_root) / x for x in json_files]
    json_check(json_files, True)

