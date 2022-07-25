import qqc
import os
from pathlib import Path

import sys
lochness_root = Path(qqc.__path__[0]).parent
scripts_dir = lochness_root / 'scripts'
sys.path.append(str(scripts_dir))

from extract_given_field_from_dicom import write_dicom_information_as_text


def read_and_delete(file_loc):
    with open(file_loc, 'r') as f:
        print(f.read())

    os.remove(file_loc)


def test_simple():
    write_dicom_information_as_text('example.dcm', '0029', '1020')


def test_with_output_file():
    write_dicom_information_as_text('example.dcm', '0029',
                                    '1020', 'test_out.txt')
    read_and_delete('test_out.txt')


