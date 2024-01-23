#!/data/pnl/kcho/anaconda3/envs/dpacc_mri/bin/python

import sys
sys.path.append('/data/predict1/home/kcho/software/qqc')
import argparse
import os
import nibabel as nb
import numpy as np
import subprocess
from pathlib import Path
from typing import List
import logging
import tempfile as tf
from InquirerPy import inquirer, prompt



logger = logging.getLogger(__name__)
logging.getLogger().addHandler(logging.StreamHandler())
data_flow_dir = Path('/data/predict1/data_from_nda')
MRI_ROOT = data_flow_dir / 'MRI_ROOT'
job_dir = MRI_ROOT / 'jobs'


def get_all_files_walk(root_dir: str, extension: str) -> List[Path]:
    '''Return a list of all json file paths under a root_dir'''
    path_list = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.' + extension) and not file.startswith('.'):
                path_list.append(Path(root) / file)

    return path_list


def parse_arguments():
    import logging
    parser = argparse.ArgumentParser()

    parser.add_argument('--qqc_html', '-qh', type=str, help='location of qqc html')

    parser.add_argument('--subses', '-ss',
                        type=str,
                        help='sub-*/ses-* text')

    parser.add_argument('--subject', '-sub',
                        type=str,
                        help='AMP-SCZ ID')

    parser.add_argument('--session', '-ses',
                        type=str,
                        help='session digit in YYYYMMDDN format')

    parser.add_argument('--print_only', '-po',
                        action='store_true',
                        help='print only')

    return parser


class AmpsczMri(object):
    def __init__(self):
        self.mri_root = MRI_ROOT
        self.rawdata_root = self.mri_root / 'rawdata'
        self.derivatives_root = self.mri_root / 'derivatives'
        self.qqc_root = self.mri_root / 'derivatives'

        if not self.rawdata_root.is_dir():
            logger.warning('No rawdata directory - could be mounting issue')

class AmpsczMriSub(AmpsczMri):
    def __init__(self, subject_id):
        super().__init__()
        self.subject = subject_id
        self.subject_rawdata_root = self.rawdata_root / \
                f"sub-{subject_id}"
        self.subject_qqc_root = self.qqc_root / \
                f"sub-{subject_id}"


class AmpsczMriSes(AmpsczMriSub):
    def __init__(self, subject_id, session_id, print_only=True):
        super().__init__(subject_id)
        self.session = session_id
        self.session_rawdata_root = self.subject_rawdata_root / \
                f"ses-{session_id}"
        self.session_qqc_root = self.subject_qqc_root / \
                f"ses-{session_id}"
        self.qqc_html = self.session_qqc_root / \
                f"qqc_summary.html"

        self.nifti_files = get_all_files_walk(self.session_rawdata_root,
                                              'nii.gz')

        # remove ignore
        self.nifti_files = [x for x in self.nifti_files
                            if x.parent.name != 'ignore']

        # remove aux
        self.nifti_files = [x for x in self.nifti_files
                            if 'auxiliary' not in x.name]

        # remove sbref and func
        self.nifti_files = [x for x in self.nifti_files
                            if x.parent.name != 'fmap']
        self.nifti_files = [x for x in self.nifti_files
                            if 'sbref' not in x.name]

        self.nifti_files_short = [x.relative_to(self.session_rawdata_root) for x in self.nifti_files]
        questions = [
            {
                'type': 'checkbox',
                'message': 'Select files',
                'name': 'files',
                'choices': [{'name': str(path), 'value': str(path)} for path in self.nifti_files_short],
            }
        ]

        answers = prompt(questions)

        selected_files = answers['files']
        if selected_files == []:
            selected_files = [str(x) for x in self.nifti_files_short]
        selected_files = [str(self.session_rawdata_root / x) for x
                in selected_files]

        command = f'fsleyes {" ".join(selected_files)}'
        print(command)


        print('rawdata root')
        print(self.session_rawdata_root)
        print()
        print('QQC report')
        print(self.qqc_html)
        print()
        print('FSLEYES command')
        for i in selected_files:
            print(i)
            if i.endswith('dwi.nii.gz') and print_only == False:
                print('splitting up images')
                split_up_and_run_fsleyes(i, print_only)
            else:
                print(f"\tfsleyes {i}")
                if not print_only:
                    os.popen(f"fsleyes {i}").read()

def split_up_and_run_fsleyes(dwi_nifti, print_only=True):
    dwi_nifti = Path(dwi_nifti)
    dwi_img = nb.load(dwi_nifti)
    dwi_data = dwi_img.get_fdata()
    dwi_bval = None

    if dwi_bval is None:
        dwi_bval = dwi_nifti.parent / (dwi_nifti.name.split('.')[0] + '.bval')
    bval_arr = np.round(np.loadtxt(dwi_bval), -2)

    bval_smoothness_dict = {}
    
    with tf.TemporaryDirectory() as tmp_dir:
        tmp_outputs = []
        for bval in np.unique(bval_arr):
            bval_index = np.where(bval_arr == bval)[0]
            data = dwi_data[:, :, :, bval_index]
            tmp_output = Path(tmp_dir) / f'{int(bval)}.nii.gz'
            nb.Nifti1Image(data, affine=dwi_img.affine,
                    header=dwi_img.header).to_filename(tmp_output)
            tmp_outputs.append(tmp_output)
        tmp_outputs = [str(x) for x in tmp_outputs]
        command = f'\tfsleyes {" ".join(tmp_outputs)} {dwi_nifti}'
        print(command)
        if not print_only:
            os.popen(command).read()

def get_available_sessions(subject):
    return [x.name for x in (MRI_ROOT / 'rawdata').glob(f"sub-{subject}/ses*")]

if __name__ == '__main__':
    # dicom_to_dpacc_bids args
    args = parse_arguments().parse_args(sys.argv[1:])
    if args.subses:
        subject = args.subses.split('/')[0].split('sub-')[1]
        session = args.subses.split('/')[1].split('ses-')[1]
        ampsczMriSes = AmpsczMriSes(subject, session, print_only=args.print_only)
    else:
        if args.subject and args.session is None:
            if 'sub-' in args.subject:
                args.subject = args.subject.split('sub-')[1]
            sessions = get_available_sessions(args.subject)
            if len(sessions) == 1:
                args.session = sessions[0].split('ses-')[1]
                print(args.session, 'is the only session')
            else:
                questions = [
                    {
                        'type': 'checkbox',
                        'message': 'Select session',
                        'name': 'session',
                        'choices': [{'name': str(session),
                                     'value': str(session)} for session
                                     in sessions],
                    }
                ]
                answers = prompt(questions)
                args.session = answers['session'][0].split('ses-')[1]
            ampsczMriSes = AmpsczMriSes(args.subject, args.session,
                    print_only=args.print_only)
        else:
            ampsczMriSes = AmpsczMriSes(args.subject, args.session,
                    print_only=args.print_only)


def test():
    ampsczMriSes = AmpsczMriSes('YA01508', '202206231')

