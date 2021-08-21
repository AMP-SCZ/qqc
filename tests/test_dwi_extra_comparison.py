import sys
import phantom_check
import os
from pathlib import Path

phantom_check_root = Path(phantom_check.__path__[0]).parent
scripts_dir = phantom_check_root / 'scripts'
test_dir = phantom_check_root / 'tests'
sys.path.append(str(scripts_dir))
sys.path.append(str(test_dir))

from dwi_extra_comparison import parse_args
from phantom_check import compare_bval_files

def test_parse_args():
    args = parse_args([
        '--bval_files',
        '/data/predict/phantom_data/human_test/human_subject_0726/dMRI_dir176_PA_22/dMRI_dir176_PA_22.bval',
        '/data/predict/phantom_data/human_test/human_subject_0729/test/22_dMRI_dir176_PA/22_dMRI_dir176_PA.bval'])

    compare_bval_files(args.bval_files)
