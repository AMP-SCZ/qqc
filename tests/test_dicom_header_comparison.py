import sys
import qqc
import os
from pathlib import Path

qqc_root = Path(qqc.__path__[0]).parent
scripts_dir = qqc_root / 'scripts'
test_dir = qqc_root / 'tests'
sys.path.append(str(scripts_dir))
sys.path.append(str(test_dir))

from dicom_header_comparison import parse_args, compare_jsons
from qqc import json_check, json_check_for_a_session
import pytest
import pandas as pd
import json
import itertools



def test_parse_args():
    args = parse_args([
        '--json_files', 'ha', 'ho'])
    print(args)


@pytest.fixture
def argparseArg():
    args = parse_args([
        '--json_files',
            'first.json', 
            'second.json'])

    return args


def test_two_jsons(argparseArg):
    dicts = []
    for i in argparseArg.json_files:
        with open(i, 'r') as f:
            dicts.append(json.load(f))

    sets = itertools.combinations(dicts, 2)

    for first_dict, second_dict in sets:
        shared_items = {k: first_dict[k] for k in first_dict if k in second_dict and first_dict[k] == second_dict[k]}
        diff_items = {k: first_dict[k] for k in first_dict if k in second_dict and first_dict[k] != second_dict[k]}
        print(diff_items)


def test_three_jsons():
    argparseArg = parse_args([
        '--json_files',
            'first.json', 'second.json', 'third.json'])

    dicts = []
    for i in argparseArg.json_files:
        with open(i, 'r') as f:
            dicts.append(json.load(f))

    names = itertools.combinations(argparseArg.json_files, 2)
    sets = itertools.combinations(dicts, 2)

    for (n1, n2), (first_dict, second_dict) in zip(names, sets):
        print(n1, n2)
        shared_items = {k: first_dict[k] for k in first_dict if k in second_dict and first_dict[k] == second_dict[k]}
        diff_items = {k: first_dict[k] for k in first_dict if k in second_dict and first_dict[k] != second_dict[k]}
        print(diff_items)


def test_json_check():
    argparseArg = parse_args([
        '--json_files',
            'first.json', 'second.json', 'third.json',
        '--print_diff', '--print_shared'])

    json_check(argparseArg.json_files,
            argparseArg.print_diff, argparseArg.print_shared)


def test_json_check_from_single_scan_session():
    argparseArg = parse_args([
        '--json_files',
            'first.json', 'second.json', 'third.json',
        '--print_diff', '--print_shared'])

    json_check_for_a_session(argparseArg.json_files,
            argparseArg.print_diff, argparseArg.print_shared)


def test_json_check_excel():
    argparseArg = parse_args([
        '--json_files',
            'first.json', 'second.json', 'third.json',
        '--print_diff', '--print_shared',
        '--save_excel', 'test.xlsx'])

    compare_jsons(argparseArg)
