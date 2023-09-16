import sys
import argparse
import os
import subprocess
from pathlib import Path
from typing import List
from dicom_to_dpacc_bids import parse_args
from qqc.pipeline import dicom_to_bids_QQC

data_flow_dir = Path('/data/predict1/data_from_nda')
MRI_ROOT = data_flow_dir / 'MRI_ROOT'
job_dir = MRI_ROOT / 'jobs'


def parse_arguments():
    parser = parse_args()
    parser.add_argument('--study_networks',
                        nargs='+', choices=['Prescient', 'Pronet'],
                        default=['Prescient', 'Pronet'],
                        help='Study networks')

    parser.add_argument('--ignore_file',
                        type=str,
                        default=MRI_ROOT / 'data_to_ignore.txt',
                        help='Ignore source text file')

    parser.add_argument('--email_recipients_file',
                        type=str,
                        default=MRI_ROOT / 'email_recipients.txt',
                        help='Email recipients text file')

    parser.add_argument('--no_email',
                        action='store_true',
                        help='Do not send email')

    parser.add_argument('--site',
                        type=str, default=None,
                        help='Run QQC on a specific site, eg) AB')

    parser.add_argument('--subject',
                        type=str, default=None,
                        help='Run QQC on a specific subject, eg) AB')

    parser.add_argument('--rerun',
                        action='store_true', default=False,
                        help='Rerun QQC')

    return parser


def read_email_recipients(email_rec: str = None):
    '''Read email receipients from scripts/email_recipients.txt'''
    if email_rec is None:
        script_loc = Path(__file__).parent
        email_rec = script_loc / 'email_recipients.txt'

    if Path(email_rec).is_file():
        with open(email_rec, 'r') as fp:
            return [x.strip() for x in fp.readlines() if '@' in x]
    else:
        print('No email receipients file found')
        return ['kc244@research.partners.org']


def read_ignore_file(ignore_file: str = None):
    if ignore_file is None:
        return []

    if Path(ignore_file).is_file():
        with open(ignore_file, 'r') as fp:
            return [x.strip() for x in fp.readlines()]
    else:
        default_file = MRI_ROOT / 'data_to_ignore.txt'
        if default_file.is_file():
            with open(ignore_file, 'r') as fp:
                return [x.strip() for x in fp.readlines()]
        else:
            return []

class ArgsNew(object):
    pass


def main(args: argparse.PARSER):
    if args.no_email:
        # args.email_report = True
        args.email_report = False
        args.additional_recipients = ['kc244@research.partners.org']
    else:
        args.email_report = True
        args.additional_recipients = read_email_recipients(
                args.email_recipients_file)

    ignore_list = read_ignore_file(args.ignore_file)

    site_str = '*' if args.site is None else f'*{args.site}'
    subject_str = '*' if args.subject is None else f'{args.subject}'

    for study_network in args.study_networks:
        PHOENIX_DIR = data_flow_dir / study_network / 'PHOENIX'
        for i in Path(PHOENIX_DIR / 'PROTECTED').glob(
            f'{site_str}/raw/{subject_str}/mri/*_MR_*_[1234].[zZ][iI][pP]'):

            filepath = str(i)
            args.input = filepath

            if filepath in ignore_list:
                continue

            print(f"reviewing {filepath} ...")
            mri_dirname = i.name
            subject = mri_dirname.split('_')[0]
            args.subject_name = subject
            year, month, day, dup = mri_dirname.split('_')[2:6]
            year, month, day, dup = year[:4], month, day, dup[0]

            session = f"{year}_{month.zfill(2)}_{day.zfill(2)}_{dup}"
            session_wo = f"{year}{month.zfill(2)}{day.zfill(2)}{dup}"
            args.session_name = session_wo
            args.bids_root = MRI_ROOT

            qqc_summary_html_file = (
                MRI_ROOT / 'derivatives' / 'quick_qc' / f'sub-{subject}' /
                f'ses-{session_wo}' / 'qqc_summary.html'
            )
            if not qqc_summary_html_file.exists():
                print(qqc_summary_html_file)
                print("=========================")
                print("QQC is not complete for")
                print(f"zipfile- {filepath}")
                print(f"subject- {subject}")
                print(f"session- {session}")
                print(f"{qqc_summary_html_file} is missing")

                dicom_to_bids_QQC(args)
                # Replace the following command with the appropriate Python code for executing dicom_to_dpacc_bids.py
                # python_cmd = [
# #                    '/usr/share/lsf/9.1/linux2.6-glibc2.3-x86_64/bin/bsub',
# #                    '-q', 'pri_pnl',
# #                    '-n', '1',
# #                    '-e', '/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/qqc_bsub.err',
# #                    '-o' '/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/qqc_bsub.out',
                    # '/data/pnl/kcho/anaconda3/bin/python',
                    # '/data/predict1/home/kcho/software/qqc/scripts/dicom_to_dpacc_bids.py',
                    # '-i', filepath,
                    # '-s', subject,
                    # '-ss', session,
                    # '-o', str(MRI_ROOT),
                    # '--email_report',
                    # '--config', '/data/predict1/data_from_nda/MRI_ROOT/standard_templates.cfg',
                    # '--force_heudiconv',
                    # '--dwipreproc', '--mriqc', '--fmriprep'] + \
                    # email_recipients

                # print(python_cmd)
                # subprocess.run(python_cmd)
                print("=========================")
                print()


if __name__ == '__main__':
    # dicom_to_dpacc_bids args
    args = parse_arguments().parse_args(sys.argv[1:])
    main(args)
