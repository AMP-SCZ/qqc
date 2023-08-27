#!/data/pnl/kcho/anaconda3/bin/python
import argparse
import configparser
import sys
import getpass
import logging
from argparse import RawTextHelpFormatter
from qqc.pipeline import dicom_to_bids_QQC
from pathlib import Path
from datetime import datetime
import re


def parse_args():
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
        description='''Convert dicoms to BIDS

    dicom_to_dpacc_bids.py \\
        --input ${raw_dicom_dir}/human_pilot/data/dicom \\
        --subject_name Pronet_PNL \\
        --session_name humanpilot \\
        --bids_root ${bids_out_dir} \\
        --standard_dir ${bids_out_dir}/rawdata/sub-standard/ses-humanpilot''',
        formatter_class=RawTextHelpFormatter)

    parser.add_argument('--input', '-i', type=str,
                        help='Raw dicom root directory or zip file.')

    parser.add_argument('--dpacc_input', '-di', type=str,
                        help='Raw dicom root directory.')

    parser.add_argument('--subject_name', '-s', type=str,
                        help='Subject name.')

    parser.add_argument('--session_name', '-ss', type=str,
                        help='Session name.')

    parser.add_argument('--bids_root', '-o', type=str,
                        help='BIDS Output directory')

    parser.add_argument('--qc_subdir', '-qs', type=str,
                        help='ExtraQC output directory name.')

    parser.add_argument('--standard_dir', '-std', type=str,
                        help='Root of a standard dataset to compare to.')

    parser.add_argument('--config', '-c', type=str,
                        default='/data/predict1/data_from_nda/MRI_ROOT/'
                                'standard_templates.cfg',
                        help='configuration file for standard tempates.')

    parser.add_argument('--mriqc', '-mriqc', action='store_true',
                        help='Run MRIQC following conversion.')

    parser.add_argument('--fmriprep', '-fmriprep', action='store_true',
                        help='Run FMRIPREP following conversion.')

    parser.add_argument('--dwipreproc', '-dwipreproc', action='store_true',
                        default=False,
                        help='Run DWI preprocessing following conversion.')

    parser.add_argument('--nifti_dir', '-nd', type=str, default=False,
                        help='Nifti root directory. If --nifti_dir is given, '
                             '--input will be ignored and dcm2niix will '
                             'not be ran.')

    parser.add_argument('--skip_dicom_rearrange', '-sdr',
                        action='store_true', default=False,
                        help='Skip dicom rearrange step.')

    parser.add_argument('--rename_dicoms', '-rd',
                        action='store_true', default=False,
                        help='Rename dicoms when rearranging dicoms')

    parser.add_argument('--force_copy_dicom_to_source', '-fc', default=False,
                        action='store_true',
                        help='Force copy dicom files to sourcedata.')

    parser.add_argument('--skip_heudiconv', '-sh', default=False,
                        action='store_true',
                        help='Skip heudiconv step.')

    parser.add_argument('--force_heudiconv', '-fh', default=False,
                        action='store_true',
                        help='Force re-running heudiconv step.')

    parser.add_argument('--skip_qc', '-sq', default=False,
                        action='store_true',
                        help='Skip quick QC step.')

    parser.add_argument('--quick_scan', '-qqs', default=False,
                        action='store_true',
                        help='Assuming single series under a directory')

    parser.add_argument('--email_report', '-e', default=False,
                        action='store_true',
                        help='Send email report')

    parser.add_argument('--additional_recipients', '-ar',
                        nargs='+',
                        type=str, default=[],
                        help='List of recipients.')

    parser.add_argument('--run_all', '-ra', default=False,
                        action='store_true',
                        help='Run all sessions.')

    return parser


if __name__ == '__main__':
    args = parse_args().parse_args(sys.argv[1:])

    config = configparser.ConfigParser()
    config.read(args.config)

    if args.run_all:
        RawTextHelpFormatter(args)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    logging.basicConfig(
        format=formatter,
        handlers=[logging.StreamHandler()])
    logging.getLogger().setLevel(logging.INFO)
        # filename=args.bids_root + '/dicom_to_dpacc_bids.log',
        # datefmt='%Y-%m-%d %H:%M:%S',
        # filemode='a',


    # build up input command to include in the log
    logging.info('*'*80)
    args_reconstruct = ''
    for d in [x for x in dir(args) if not x.startswith('_')]:
        args_reconstruct += f' --{d}={getattr(args, d)}'
    logging.info(f'command used: \ndicom_to_dpacc_bids.py {args_reconstruct}')
    logging.info('Dicom to DPACC BIDS conversion started')

    dicom_to_bids_QQC(args)
    logging.info('Completed')

