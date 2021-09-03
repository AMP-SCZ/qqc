#!/data/pnl/kcho/anaconda3/bin/python
import pydicom
import argparse
import sys


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
            description='Extract extra information from dicom')

    # image input related options
    parser.add_argument('--dicom_file', '-df', type=str,
            help='Path of dicom file.')

    # header information
    parser.add_argument('--group_number', '-gn', type=str,
            help='Group number to extract information from.')
    parser.add_argument('--element_number', '-en', type=str,
            help='Element number to extract information from.')

    # output
    parser.add_argument('--output_file', '-o', type=str, default=False,
            help='Path of a text file to store the information.')

    args = parser.parse_args(argv)
    return args


def write_dicom_information_as_text(dicom_file: str,
                                    group_number: str,
                                    element_number: str,
                                    output_file: str = False):
    '''Write dicom information as text'''

    dicom_f = pydicom.read_file(dicom_file)
    info = dicom_f.get((group_number, element_number))
    extracted_text = info.value.decode(errors='ignore').split(
            '### ASCCONV')[1]

    if output_file:
        with open(output_file, 'w') as f:
            f.write(extracted_text)
    else:
        print(extracted_text)



if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    write_dicom_information_as_text(args.dicom_file, args.group_number,
                                    args.element_number, args.output_file)


