#!/usr/bin/env python
import argparse
import sys
from qqc import compare_bval_files

def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(description='Extra comparisons')

    # image input related options
    parser.add_argument('--bval_files', type=str, nargs='+',
            help='List of bval files created from dcm2niix.')

    # extra options
    args = parser.parse_args(argv)
    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    if args.bval_files:
        compare_bval_files(args.bval_files)
