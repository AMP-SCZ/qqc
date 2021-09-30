import argparse
import sys
import pandas as pd

from phantom_check.dicom_files import get_dicom_files_walk, \
        get_diff_in_csa_for_all_measures

def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
            description= 'Extracts CSA header as a csv file.')

    # image input related options
    parser.add_argument('--input', '-i', type=str,
                        help='Raw dicom root directory')

    parser.add_argument(
            '--output', '-o', type=str,
            help='Output csv file.')

    parser.add_argument(
            '--diff_only', '-do', action='store_true', default=False,
            help='Only save variables that are different across scans.')

    parser.add_argument(
            '--common_only', '-co', action='store_true', default=False,
            help='Only save variables that are consistent across scans.')


    # extra options
    args = parser.parse_args(argv)
    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    df = get_dicom_files_walk(args.input, True)
    csa_diff_df, csa_common_df = get_diff_in_csa_for_all_measures(
            df, get_same=True)

    if args.diff_only:
        csa_diff_df.to_csv(args.output)

    elif args.common_only:
        csa_common_df.to_csv(args.output)
    
    else:
        tmp = pd.concat([csa_diff_df, csa_common_df])
        tmp.to_csv(args.output)

