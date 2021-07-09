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


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(description='Summarize phantom')

    # image input related options
    parser.add_argument('--json_files', type=str, nargs='+',
            help='List of json files created from dcm2niix.')

    parser.add_argument('--nifti_prefixes', type=str, nargs='+',
            help='List of nifti image prefixes to catch relevant json files.')

    parser.add_argument('--multi_file_dir', type=str,
            help='Path of a directory, where there are unique json or dicom '
                 'files to be compared to each other.')

    parser.add_argument('--print_diff', action='store_true',
            help='Print different items between the json_files')

    parser.add_argument('--print_shared', action='store_true',
            help='Print the same items between the json_files')

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


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    json_check(args.json_files, args.print_diff, args.print_shared)
