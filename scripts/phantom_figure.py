#!/usr/bin/env python

from phantom_check.utils.visualize import create_b0_signal_figure
from phantom_check.utils.visualize import create_image_signal_figure
from phantom_check.utils.files import get_diffusion_data_from_dicom_dir
from phantom_check.utils.files import get_diffusion_data_from_nifti_prefix
from phantom_check.utils.files import get_diffusion_data_from_nifti_dir
from phantom_check.utils.files import get_nondmri_data

import argparse
from pathlib import Path
import sys


def parse_args():
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(description='Summarize phantom')

    # mode
    parser.add_argument('--mode', type=str, required=True,
            choices=['dmri', 'general_4d'],
            help='Select mode')

    # image input related options
    parser.add_argument('--dicom_dirs', type=str, nargs='+',
            help='List of dicom directories to plot summary. They will be '
                 'converted to nifti using dcm2niix to new directories.')
    parser.add_argument('--nifti_prefixes', type=str, nargs='+',
            help='List of nifti image prefixes to plot summary from.')
    parser.add_argument('--nifti_dirs', type=str, nargs='+',
            help='List of directories that contain unique nifti image')

    # extra options
    parser.add_argument('--names', type=str, nargs='+',
            help='List of name for each given dicom dirs, nifti prefixes or '
                 'nifti dirs')
    parser.add_argument('--store_nifti', action='store_true',
            help='Keep outputs of dcm2niix for later use.')
    parser.add_argument('--b0thr', type=int, default=50,
            help='b0 threshold, default=50')
    parser.add_argument('--fig_num_in_row', type=int, default=3,
            help='Number of columns in the figure')
    parser.add_argument('--wide_fig', action='store_true',
            help='Create wide figure')
    parser.add_argument('--out_image', type=str, help='Out image file')


    args = parser.parse_args()
    return args


def dmri_b0_summary(args):
    if args.dicom_dirs:
        function = get_diffusion_data_from_dicom_dir
        vars = args.dicom_dirs
    elif args.nifti_prefixes:
        function = get_diffusion_data_from_nifti_prefix
        vars = args.nifti_prefixes
    elif args.nifti_dirs:
        function = get_diffusion_data_from_nifti_dir
        vars = args.nifti_dirs
    else:
        sys.exit('Data input needs to be provided. Provide one of '
        '--dicom_dirs, --nifti_prefixes or --nifti_dirs. Exiting.')

    dataset = []
    for num, var in enumerate(vars):
        name = args.names[num] if args.names else Path(var).name
        data, bval_arr = function(var, name, args.b0thr, args.store_nifti)
        dataset.append((data, bval_arr, name))

    create_b0_signal_figure(dataset, args.out_image,
                            True, args.fig_num_in_row, args.wide_fig)

def fmri_summary(args):
    function = get_nondmri_data
    if args.dicom_dirs:
        dtype = 'dicom_dir'
        vars = args.dicom_dirs
    elif args.nifti_prefixes:
        dtype = 'nifti_prefix'
        vars = args.nifti_prefixes
    elif args.nifti_dirs:
        dtype = 'nifti_dir'
        vars = args.nifti_dirs
    else:
        sys.exit('Data input needs to be provided. Provide one of '
                 '--dicom_dirs, --nifti_prefixes or --nifti_dirs. Exiting.')

    dataset = []
    for num, var in enumerate(vars):
        name = args.names[num] if args.names else Path(var).name
        data = function(var, dtype, name, args.store_nifti)
        dataset.append((data, name))

    create_image_signal_figure(dataset, args.out_image,
                               True, args.fig_num_in_row,
                               args.wide_fig)


if __name__ == '__main__':
    args = parse_args()

    if args.mode == 'dmri':
        dmri_b0_summary(args)

    if args.mode == 'general_4d':
        fmri_summary(args)
