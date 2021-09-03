#!/data/pnl/kcho/anaconda3/bin/python
import pydicom
import argparse
import sys


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
            description='Extract extra information from dicom')

    # image input related options
    parser.add_argument('--dicom_files', '-df', type=str, nargs='+',
            help='List of dicom files.')

    # header information
    parser.add_argument('--group_number', '-gn', type=str,
            help='Group number to extract information from.')
    parser.add_argument('--element_number', '-en', type=str,
            help='Element number to extract information from.')

    # output
    parser.add_argument('--output', '-o', type=str,
            help='Output text file to store information.')

    args = parser.parse_args(argv)
    return args


def write_dicom_information_as_text(dicom_file: str, group_number: str,
                                    element_number: str, output_file: str):
    '''Write dicom information as text'''

    with open(output_file, 'w') as f:
        dicom_f = pydicom.read_file(dicom_file)
        a = dicom_f.get((group_number, element_number))
        f.write(a.value.decode(errors='ignore'))


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    dicom_f = pydicom.read_file(sys.argv[1])


