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

from qqc.bids_files import jsons_from_bids_to_df
        
scripts_path = Path(__file__).parent.parent.parent / 'scripts'
import sys
sys.path.append(str(scripts_path))
from dicom_to_dpacc_bids import check_num_order_of_series

pd.set_option('max_columns', 10)


def test_jsons_from_bids_to_df():
    session_dir = '/data/predict/phantom_human_pilot/' \
                  'sub-ProNETUCLA/ses-humanpilot'
    df = jsons_from_bids_to_df(session_dir)

    check_num_order_of_series(df, Path('.'), False)


