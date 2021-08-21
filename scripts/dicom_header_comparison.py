#!/usr/bin/env python

from phantom_check.utils.files import get_jsons_from_dicom_dirs
from phantom_check import json_check

import sys
import argparse
from pathlib import Path
import pandas as pd


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(description='Summarize phantom')

    # image input related options
    parser.add_argument('--dicom_dirs', type=str, nargs='+',
            help='List of dicom directories to plot summary. They will be '
                 'converted to nifti using dcm2niix to new directories.')

    parser.add_argument('--json_files', type=str, nargs='+',
            help='List of json files created from dcm2niix.')

    parser.add_argument(
            '--from_single_session', action='store_true', default=False,
            help='Switch to use if all the json_files are from a single scan '
                 'session')

    parser.add_argument('--multi_file_dir', type=str,
            help='Path of a directory, where there are unique json or dicom '
                 'files to be compared to each other.')

    parser.add_argument('--store_nifti', action='store_true',
            help='Keep outputs of dcm2niix for later use.')

    parser.add_argument('--print_diff', action='store_true',
            help='Print different items between the json_files')

    parser.add_argument('--print_shared', action='store_true',
            help='Print the same items between the json_files')

    parser.add_argument('--save_excel', type=str,
            help='Save the diff and shared table to an excel file')

    # extra options
    parser.add_argument('--names', type=str, nargs='+',
            help='List of name for each given dicom dirs, nifti prefixes or '
                 'nifti dirs')

    # extra options
    args = parser.parse_args(argv)
    return args


def compare_jsons(args):
    if args.dicom_dirs:
        json_files = get_jsons_from_dicom_dirs(args.dicom_dirs,
                                               args.names,
                                               args.save_outputs)
        df_all_diff, df_all_shared = json_check(
                json_files, args.from_single_session, args.print_diff, args.print_shared)

    elif args.json_files:
        df_all_diff, df_all_shared = json_check(
                args.json_files, args.from_single_session, args.print_diff, args.print_shared)

    elif args.multi_file_dir:
        json_files = Path(args.multi_file_dir).glob('*json')
        df_all_diff, df_all_shared = json_check(
                json_files, args.from_single_session, args.print_diff, args.print_shared)

    else:
        sys.exit('Please provide either --dicom_dirs or --json_files')

    if args.save_excel:
        with pd.ExcelWriter(args.save_excel) as writer:
            df_all_diff.to_excel(writer, sheet_name='diff')
            df_all_shared.to_excel(writer, sheet_name='shared')


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    compare_jsons(args)
