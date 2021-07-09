#!/usr/bin/env python

import argparse
from pathlib import Path
import subprocess
import sys
import os
import nibabel as nb
import numpy as np
import matplotlib.pyplot as plt
import tempfile
import shutil
from typing import List
import math
import pandas as pd
import itertools
import json
from phantom_figure import convert_to_img


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(description='Summarize phantom')

    # image input related options
    parser.add_argument('--dicom_dirs', type=str, nargs='+',
            help='List of dicom directories to plot summary. They will be '
                 'converted to nifti using dcm2niix to new directories.')

    parser.add_argument('--json_files', type=str, nargs='+',
            help='List of json files created from dcm2niix.')

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


def pretty_print_dict(input_dict: dict):
    '''Pretty print dictionary'''
    with tempfile.NamedTemporaryFile(suffix='.json', delete=True) as tmpfile:
        with open(tmpfile.name, 'w') as f:
            json.dump(input_dict, f,
                    sort_keys=False, indent='  ', separators=(',', ': '))

        with open(tmpfile.name, 'r') as f:
            lines = f.readlines()
            for i in lines:
                print(i.strip('\n'))


def json_check(json_files: List[str],
               print_diff: bool = True,
               print_shared: bool = False):
    '''Iteratively compare between MR protocol json files and print outputs'''
    dicts = []
    for i in json_files:
        with open(i, 'r') as f:
            dicts.append(json.load(f))

    names = itertools.combinations(json_files, 2)
    sets = itertools.combinations(dicts, 2)

    df_all_diff = pd.DataFrame()
    df_all_shared = pd.DataFrame()
    for (name_1, name_2), (first_dict, second_dict) in zip(names, sets):
        diff_items = {k: first_dict[k] for k in first_dict
                      if k in second_dict and first_dict[k] != second_dict[k]}
        shared_items = {k: first_dict[k] for k in first_dict
                        if k in second_dict and
                        first_dict[k] == second_dict[k]}

        df_diff = pd.DataFrame.from_dict(diff_items, orient='index')
        df_shared = pd.DataFrame.from_dict(shared_items, orient='index')
        df_diff.columns = [f'{name_1} (vs {name_2})']
        df_shared.columns = [f'{name_1} (vs {name_2})']
        df_all_diff = pd.concat([df_all_diff, df_diff], axis=1)
        df_all_shared = pd.concat([df_all_shared, df_shared], axis=1)

    if print_diff:
        print(f'Different items')
        print('='*80)
        # pretty_print_dict(diff_items)
        print(df_all_diff)
        print()
        print()
        print('='*80)
        print()

    if print_shared:
        print(f'The same items included in both each comparison')
        print('='*80)
        # pretty_print_dict(shared_items)
        print(df_all_shared)
        print()
        print()
        print('='*80)
        print()

    return (df_all_diff, df_all_shared)


def get_jsons_from_dicom_dirs(dicom_dirs: List[str],
                              names: List[str] = None,
                              save_outputs: bool = True):
    json_files = []
    for num, dicom_dir in enumerate(args.dicom_dirs):
        name = names[num] if names else Path(dicom_dir).name
        temp_dir = tempfile.TemporaryDirectory()
        convert_to_img(dicom_dir, temp_dir.name, name)
        json_files.append(Path(temp_dir) / (name + '.json'))

        if args.save_outputs:
            shutil.copytree(temp_dir.name, name)

        temp_dir.cleanup()

    return json_files


def compare_jsons(args):
    if args.dicom_dirs:
        json_files = get_jsons_from_dicom_dirs(args.dicom_dirs,
                                               args.names,
                                               args.save_outputs)
        df_all_diff, df_all_shared = json_check(
                json_files, args.print_diff, args.print_shared)

    elif args.json_files:
        df_all_diff, df_all_shared = json_check(
                args.json_files, args.print_diff, args.print_shared)

    elif args.multi_file_dir:
        json_files = Path(args.multi_file_dir).glob('*json')
        df_all_diff, df_all_shared = json_check(
                json_files, args.print_diff, args.print_shared)

    else:
        sys.exit('Please provide either --dicom_dirs or --json_files')

    if args.save_excel:
        with pd.ExcelWriter(args.save_excel) as writer:
            df_all_diff.to_excel(writer, sheet_name='diff')
            df_all_shared.to_excel(writer, sheet_name='shared')
        

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    compare_jsons(args)
