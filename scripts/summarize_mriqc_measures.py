#!/usr/bin/env python

from phantom_check.utils.files import \
        load_and_filter_anat_qc_from_open_data, \
        load_anat_jsons_from_mriqc, \
        add_open_data_qc_measures
from phantom_check.utils.visualize import \
        plot_anat_jsons_from_mriqc_with_opendata

import sys
import argparse
from pathlib import Path
import pandas as pd


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(description='Summarize mriqc')

    # image input related options
    parser.add_argument(
            '--mri_qc_jsons', type=str, nargs='+',
            help='List of MRIQC output json file to summarize.')

    parser.add_argument(
            '--opendata_csv', type=str,
            help='Path of open data csv file of the same modality as the '
                 '--mri_qc_jsons.')

    parser.add_argument('--out_image', type=str, help='Out image file')

    # extra options
    args = parser.parse_args(argv)
    return args


def plot_with_open_data(args: argparse):
    df_open = load_and_filter_anat_qc_from_open_data(args.opendata_csv)
    df_mri_qc = load_anat_jsons_from_mriqc(args.mri_qc_jsons)
    df = add_open_data_qc_measures(df_mri_qc, df_open)
    g = plot_anat_jsons_from_mriqc_with_opendata(df, args.out_image)


if __name__ == '__main__':
    args = parse_args()
    plot_with_open_data(args)

