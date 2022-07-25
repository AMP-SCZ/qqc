import sys
import qqc
import os
from pathlib import Path

qqc_root = Path(qqc.__path__[0]).parent
scripts_dir = qqc_root / 'scripts'
test_dir = qqc_root / 'tests'
sys.path.append(str(scripts_dir))
sys.path.append(str(test_dir))

from dwi_extra_comparison import parse_args
from qqc import compare_bval_files

def test_parse_args():
    args = parse_args([
        '--bval_files',
        'first.bval',
        'second.bval'])

    compare_bval_files(args.bval_files)
