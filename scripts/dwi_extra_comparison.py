#!/usr/bin/env python
import argparse
import sys
from qqc.qqc.json import compare_bval_files
from qqc.utils.files import get_files_from_json
import pandas as pd
pd.set_option('display.max_columns', 50)

def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(description='Extra comparisons')

    # image input related options
    parser.add_argument('--bval_files', '-b', type=str, nargs='+',
            help='List of bval files created from dcm2niix.')

    parser.add_argument('--json_files', '-j', type=str, nargs='+',
            help='List of bval files created from dcm2niix.')

    parser.add_argument('--output_csv', '-o', type=str,
            help='Save comparison to a csv')

    # extra options
    args = parser.parse_args(argv)
    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    if args.bval_files:
        df = compare_bval_files(args.bval_files)
        print(df)

    if args.json_files:
        bval_files = get_files_from_json(args.json_files, 'b0', 'bval')
        df = compare_bval_files(bval_files)
        print(df)

    if args.output_csv:
        df.to_csv(args.output_csv)
