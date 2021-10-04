from pathlib import Path
scripts_path = Path(__file__).parent.parent.parent / 'scripts'
import sys
import re
sys.path.append(str(scripts_path))

from dicom_to_dpacc_bids import dicom_to_bids, parse_args, \
        compare_data_to_standard, quick_figures, dicom_to_bids_with_quick_qc
from phantom_check.dicom_files import get_dicom_files_walk, \
        get_diff_in_csa_for_all_measures

from phantom_check.utils.files import get_diffusion_data_from_nifti_dir
from phantom_check.utils.files import load_data_bval
from phantom_check.utils.visualize import create_b0_signal_figure, \
        create_image_signal_figure
from phantom_check.utils.files import get_nondmri_data
import pandas as pd

raw_dicom_dir = Path(__file__).parent.parent.parent / 'data' / \
        'dicom_raw_source'

standard_dicom_dir = Path(__file__).parent.parent.parent / 'data' / \
        'dicom_raw_source'



def test_args():
    args = parse_args(['-i', str(raw_dicom_dir),
        '-s', 'testsubject',
        '-ss', 'testsession',
        '-o', 'test'])


def test_dicom_to_bids_default():
    args = parse_args(['-i', str(raw_dicom_dir),
        '-s', 'testsubject',
        '-ss', 'testsession',
        '-o', 'testroot'])

    dicom_to_bids(args.input_dir, args.subject_name,
                  args.session_name, args.output_dir)


def test_dicom_to_bids_different_name():
    args = parse_args(['-i', str(raw_dicom_dir),
        '-s', 'PronetLA123456',
        '-ss', '001',
        '-o', 'testroot'])

    dicom_to_bids(args.input_dir, args.subject_name,
                  args.session_name, args.output_dir)


def test_dicom_to_bids_make_standard():
    args = parse_args(['-i', str(standard_dicom_dir),
        '-s', 'ProNET_Yale_Prisma_fit',
        '-ss', 'phantom',
        '-o', 'testroot'])

    dicom_to_bids(args.input_dir, args.subject_name,
                  args.session_name, args.output_dir)


def test_compare_data_to_standard():
    args = parse_args(['-i', str(raw_dicom_dir),
        '-s', 'testsubject',
        '-ss', 'testsession',
        '-o', 'testroot',
        '-std', 'testroot/sub-ProNETYalePrismafit'])

    subject_dir = Path(args.output_dir) / ('sub-' + re.sub(
            '_-', ' ', args.subject_name))
    qc_out_dir = Path(args.output_dir) / 'quick_qc' / \
            subject_dir.name / args.session_name
    qc_out_dir.mkdir(exist_ok=True, parents=True)

    compare_data_to_standard(subject_dir, args.standard_dir, qc_out_dir)


def test_csa_extraction():
    args = parse_args(['-i', str(raw_dicom_dir),
        '-s', 'testsubject',
        '-ss', 'testsession',
        '-o', 'testroot',
        '-std', 'testroot/sub-ProNETYalePrismafit'])

    df = get_dicom_files_walk(args.input_dir, True)
    csa_diff_df, csa_common_df = get_diff_in_csa_for_all_measures(
            df, get_same=True)

    subject_dir = Path(args.output_dir) / ('sub-' + re.sub(
            '_-', ' ', args.subject_name))
    qc_out_dir = Path(args.output_dir) / 'quick_qc' / \
            subject_dir.name / args.session_name
    qc_out_dir.mkdir(exist_ok=True, parents=True)

    tmp = pd.concat([csa_diff_df, csa_common_df])
    tmp.to_csv(qc_out_dir / 'csa_headers.csv')


def test_figure_extraction():
    args = parse_args(['-i', str(raw_dicom_dir),
        '-s', 'testsubject',
        '-ss', 'testsession',
        '-o', 'testroot',
        '-std', 'testroot/sub-ProNETYalePrismafit'])

    subject_dir = Path(args.output_dir) / ('sub-' + re.sub(
            '_-', ' ', args.subject_name))
    qc_out_dir = Path(args.output_dir) / 'quick_qc' / \
            subject_dir.name / args.session_name
    qc_out_dir.mkdir(exist_ok=True, parents=True)

    quick_figures(subject_dir, args.session_name, qc_out_dir)



def test_whole_flow():
    args = parse_args(['-i', str(raw_dicom_dir),
        '-s', 'whole_flow',
        '-ss', 'testsession',
        '-o', 'testroot',
        '-std', 'testroot/sub-ProNETYalePrismafit'])

    dicom_to_bids_with_quick_qc(args)


