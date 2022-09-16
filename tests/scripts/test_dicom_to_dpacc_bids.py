from pathlib import Path
scripts_path = Path(__file__).parent.parent.parent / 'scripts'
import sys
import re
sys.path.append(str(scripts_path))

from dicom_to_dpacc_bids import parse_args
from qqc.pipeline import dicom_to_bids_QQC
from qqc.dicom_files import get_dicom_files_walk, \
        get_diff_in_csa_for_all_measures

from qqc.utils.files import get_diffusion_data_from_nifti_dir
from qqc.utils.files import load_data_bval
from qqc.utils.visualize import create_b0_signal_figure, \
        create_image_signal_figure
from qqc.utils.files import get_nondmri_data
import pandas as pd
import socket
import numpy as np

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if socket.gethostname() == 'mbp16':
    raw_dicom_dir = Path(__file__).parent.parent.parent / 'data' / \
            'dicom_raw_source'

    standard_dicom_dir = Path(__file__).parent.parent.parent / 'data' / \
            'dicom_raw_source'
else:

    # raw_dicom_dir = Path('/data/predict/phantom_data/kcho/tmp')
    # standard_dicom_dir = Path(__file__).parent.parent.parent / 'data' / \
            # 'dicom_raw_source'
    raw_dicom_dir = Path('/data/predict/phantom_data/kcho/tmp/PHANTOM_20211022')
    standard_dicom_dir = Path('/data/predict/phantom_human_pilot/rawdata/sub-ProNETUCLA/ses-humanpilot')



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

def test_dicom_to_bids_new_dir():
    args = parse_args(['-i', str(raw_dicom_dir),
        '-s', 'testsubject',
        '-ss', 'testsession',
        '-o', 'testroot_new'])

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


def test_compare_data_to_standard_all_nifti():

    subject_dir = Path('/data/predict/phantom_human_pilot/'
                       'sub-ProNETSeoul/ses-phantom')
    standard_dir = Path('/data/predict/phantom_human_pilot/'
                        'sub-ProNETUCLA/ses-humanpilot')

    qc_out_dir = Path('tmp')
    qc_out_dir.mkdir(exist_ok=True)
    compare_data_to_standard(subject_dir, standard_dir, qc_out_dir)


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


def test_whole_flow_example():
    args = parse_args(['-i',
            '/data/predict/kcho/flow_test/Prescient/PHOENIX/PROTECTED'
            '/PrescientSG/raw/SG00055/mri/SG00055_MR_2022_01_19_1',
        '-s', 'SG00055',
        '-ss', '202201191',
        '-o', '/data/predict/kcho/flow_test/MRI_ROOT',
        '-std',
            '/data/predict/phantom_human_pilot/rawdata/sub-ProNETUCLA/'
            'ses-humanpilot'])

    dicom_to_bids_with_quick_qc(args)


def test_whole_flow_example():
    args = parse_args(['-i',
            '/data/pnl/kcho/ha/20211117#C414_dicom',
        '-s', 'SG00055',
        '-ss', '202201191',
        '-o', '/data/predict/kcho/flow_test/MRI_ROOT',
        '-std',
            '/data/predict/phantom_human_pilot/rawdata/sub-ProNETUCLA/'
            'ses-humanpilot'])

    dicom_to_bids_with_quick_qc(args)


def test_whole_flow_sf_example():
    args = parse_args(['-i',
            '/data/predict/kcho/flow_test/Pronet/PHOENIX/PROTECTED'
            '/PronetSF/raw/SF11111/mri/SF11111_MR_2022_01_26_1',
        '-s', 'SF11111',
        '-ss', '202201261',
        '-o', '/data/predict/kcho/flow_test/MRI_ROOT',
        '-std',
            '/data/predict/phantom_human_pilot/rawdata/sub-ProNETUCLA/'
            'ses-humanpilot'])

    dicom_to_bids_with_quick_qc(args)


def test_whole_flow_nl_example():
    args = parse_args(['-i',
            '/data/predict/kcho/flow_test/Pronet/PHOENIX/PROTECTED'
            '/PronetNL/raw/NL00000/mri/NL00000_MR_2021_12_07_1',
        '-s', 'NL00000',
        '-ss', '202112071',
        '-o', '/data/predict/kcho/flow_test/MRI_ROOT',
        '--dwipreproc'])
        # '-std',
            # '/data/predict/phantom_human_pilot/rawdata/sub-ProNETUCLA/'
            # 'ses-humanpilot',
        # '--dwipreproc', '--mriqc', '--fmriprep'])

    dicom_to_bids_with_quick_qc(args)


def test_whole_flow_igor():
    sourcedata_dir = '/data/predict/data_from_nda_dev/MRI_ROOT/sourcedata'
    sourcedata = Path(sourcedata_dir) / 'JE00068/ses-202206282'
    args = parse_args(['-i', str(sourcedata),
        '-s', 'NL00000',
        '-ss', '202112071',
        '-o', '/data/predict/data_from_nda_dev/MRI_ROOT',
        '--skip_dicom_rearrange', 
        ])
        # '-std',
            # '/data/predict/phantom_human_pilot/rawdata/sub-ProNETUCLA/'
            # 'ses-humanpilot',
        # '--dwipreproc', '--mriqc', '--fmriprep'])

    dicom_to_bids_with_quick_qc(args)


def test_whole_flow_me_example():
    args = parse_args(['-i',
            '/data/predict/kcho/flow_test/Prescient/PHOENIX/PROTECTED/PrescientME/raw/ME00005/mri/1.1.28 PRESCIENT',
        '-s', 'ME00005',
        '-ss', '202112081',
        '-o', '/data/predict/kcho/flow_test/MRI_ROOT',
        '-std',
            '/data/predict/phantom_human_pilot/rawdata/sub-ProNETUCLA/'
            'ses-humanpilot',
        '--dwipreproc', '--mriqc', '--fmriprep'])
        # '--dwipreproc', '--mriqc', '--fmriprep'])

    dicom_to_bids_with_quick_qc(args)


def test_whole_flow_GE_data():
    args = parse_args(['-i',
            '/data/predict/phantom_data/site_data/ProNET_Calgary_GE/human_pilot/dicom/second_transfer/AMP-SCZ_01/AMP-SCZ_01',
        '-s', 'CG',
        '-ss', '1',
        '-o', '/data/predict/phantom_data/site_data/ProNET_Calgary_GE/human_pilot/dicom/second_transfer/MRI_ROOT2',
        '--skip_heudiconv', '--skip_dicom_rearrange'])
        # '--dwipreproc', '--mriqc', '--fmriprep'])

    dicom_to_bids_with_quick_qc(args)
        
def test_within_phantom_qc():
    args = parse_args(['-i', str(raw_dicom_dir),
        '-s', 'whole_flow',
        '-ss', 'testsession',
        '-o', 'testroot',
        '-std', 'testroot/sub-ProNETYalePrismafit'])

    # dicom_to_bids_with_quick_qc(args)
    # variable settings
    subject_dir = Path(args.output_dir) / ('sub-' + re.sub(
            '[_-]', '', args.subject_name))
    qc_out_dir = Path(args.output_dir) / 'quick_qc' / \
            subject_dir.name / args.session_name
    qc_out_dir.mkdir(exist_ok=True, parents=True)

    within_phantom_qc(subject_dir, qc_out_dir)


def test_within_phantom_qc_smooth():
    args = parse_args(['-i', str(raw_dicom_dir),
        '-s', 'whole_flow',
        '-ss', 'testsession',
        '-o', 'testroot',
        '-std', '/data/predict/phantom_human_pilot/rawdata/sub-ProNETYalePrismafit/ses-phantom'])


    print(args)
    dicom_to_bids_with_quick_qc(args)


def test_within_phantom_nifti_snapshot():
    args = parse_args(['-i', str(raw_dicom_dir),
        '-s', 'whole_flow',
        '-ss', 'testsession',
        '-o', 'testroot',
        '-std', '/data/predict/phantom_human_pilot/rawdata/sub-ProNETYalePrismafit/ses-phantom'])

    from nifti_snapshot import nifti_snapshot
    import re
    t1w_norm = Path(args.output_dir) / 'rawdata' / \
            'sub-wholeflow' / 'ses-testsession' / 'anat' / \
            'sub-wholeflow_ses-testsession_rec-norm_run-1_T1w.nii.gz'

    outfile = './test.png'
    
    fig = nifti_snapshot.SimpleFigure(
        image_files = [t1w_norm],
        title = 't1w_norm_title',
        make_transparent_zero = True,
        cbar_width = 0.5,
        cbar_title = 'cbar title',
        output_file = outfile,
    )

        # percentile = [0.5]
        # volumes = args.volumes,
    # # these two lines have to be in the script or in your ~/.bashrc to use the function
    # export PYTHONPATH=/data/predict/phantom_data/softwares/nifti-snapshot:${PYTHONPATH}
    # export PATH=/data/predict/phantom_data/softwares/nifti-snapshot/scripts:${PATH}

    # mkdir nifti_snapshot
    # for i in */*nii.gz
    # do
        # name=`basename ${i%.nii.gz}`
        # nifti_snapshot -i ${i} -o nifti_snapshot/${name}.png -c gray
    # done


    # # if you want to visualize specific volume (vol==5) for a 4d nifti file
    # nifti_snapshot -i ${i} -o nifti_snapshot/${name}.png -c gray -volumes 5


    # # if you want to use different percentile to threshold the image (minimum threshold for 10th percentile, maximum threshold for 95th percentile - Default is 5 and 10)
    # nifti_snapshot -i ${i} -o nifti_snapshot/${name}.png -c gray --volumes 5 –intensity_percentile 10 95


    print(args)
    # dicom_to_bids_with_quick_qc(args)



def test_within_phantom_partial_rescan():
    args = parse_args(['-i', '/data/predict/phantom_data/site_data/Prescient_Jena_Prisma/phantom/data/dicom/1.3.12.2.1107.5.2.43.67036.30000021112408332049800000006',
        '-s', 'whole_flow',
        '-ss', 'partialrescan',
        '-o', 'testroot',
        '-std', '/data/predict/phantom_human_pilot/rawdata/sub-ProNETYalePrismafit/ses-phantom',
        '--partial_rescan'])

    print(args)
    dicom_to_bids_with_quick_qc(args)


def test_within_phantom_quick_qc_rerun():
    args = parse_args(['-i', str(raw_dicom_dir),
        '-s', 'whole_flow',
        '-ss', 'testsession',
        '-o', 'testroot',
        '-std', '/data/predict/phantom_data/phantom_data_BIDS/sub-ProNETUCLA/ses-humanpilot'])

    args.session_name = re.sub('[_-]', '', args.session_name)
    df_full = get_dicom_files_walk(args.input_dir, True)

    # assert number of series
    # QC
    # settings
    subject_dir = Path(args.output_dir) / ('sub-' + re.sub(
            '[_-]', '', args.subject_name))
    session_dir = subject_dir / ('ses-' + args.session_name)
    qc_out_dir = Path(args.output_dir) / 'quick_qc' / \
            subject_dir.name / args.session_name
    qc_out_dir.mkdir(exist_ok=True, parents=True)

    # # within data QC
    # print('Within phantom QC')
    # within_phantom_qc(session_dir, qc_out_dir)

    # # CSA extraction
    # print('CSA extraction')
    # df_with_one_series = pd.concat([
        # x[1].iloc[0] for x in df_full.groupby('series_num')], axis=1).T
    # save_csa(df_with_one_series, qc_out_dir)

    # if args.standard_dir:
        # print('Comparison to standard')
        # compare_data_to_standard(session_dir, args.standard_dir, qc_out_dir)

    print('Creating summary figures')
    quick_figures(session_dir, qc_out_dir)

    # dicom_to_bids_with_quick_qc(args)
    # # variable settings
    # subject_dir = Path(args.output_dir) / ('sub-' + re.sub(
            # '[_-]', '', args.subject_name))
    # qc_out_dir = Path(args.output_dir) / 'quick_qc' / \
            # subject_dir.name / args.session_name
    # qc_out_dir.mkdir(exist_ok=True, parents=True)


def test_check_number_of_series():
    print(raw_dicom_dir / 'PHANTOM_20211022')
    args = parse_args(['-i', str(raw_dicom_dir / 'PHANTOM_20211022'),
        '-s', 'whole_flow',
        '-ss', 'testsession',
        '-o', 'testroot',
        '-std', '/data/predict/phantom_data/phantom_data_BIDS/sub-ProNETUCLA/ses-humanpilot'])

    args.session_name = re.sub('[_-]', '', args.session_name)
    # df_full = get_dicom_files_walk(args.input_dir, True)

    if Path('tmp_df.csv').is_file():
        df_full = pd.read_csv('tmp_df.csv', index_col = 0)
    else:
        df_full = get_dicom_files_walk(args.input_dir)
        df_full.to_csv('tmp_df.csv')

    check_num_order_of_series(df_full, Path('.'))


def test_jena_with_new_dcm2niix():
    args = parse_args([
        '-i', '/data/predict/data_from_nda_dev/MRI_ROOT/sourcedata/JE00068/ses-202206282',
        '-s', 'JE00068',
        '-ss', '202206282',
        '-o', 'testroot',
        '-std', '/data/predict/phantom_human_pilot/rawdata/sub-ProNETYalePrismafit/ses-phantom',
        ])

    print(args)
    dicom_to_bids_QQC(args)


def test_yale_followup():
    args = parse_args([
        '-i', '/data/predict/data_from_nda/Pronet/PHOENIX/PROTECTED/PronetYA/raw/YA01508/mri/YA01508_MR_2022_08_26_1',
        '-s', 'YA01508',
        '-ss', '202208261',
        '-o', '/data/predict/data_from_nda/MRI_ROOT',
        '-std', '/data/predict/data_from_nda/MRI_ROOT/rawdata/sub-YA01508/ses-202206231',
        ])

    print(args)
    dicom_to_bids_QQC(args)


def test_yale_followup_pipeline():
    args = parse_args([
        '-i', '/data/predict/data_from_nda/Pronet/PHOENIX/PROTECTED/PronetYA/raw/YA01508/mri/YA01508_MR_2022_08_26_1',
        '-s', 'YA01508',
        '-ss', '202208261',
        '-o', '/data/predict/data_from_nda/MRI_ROOT',
        '-std', '/data/predict/data_from_nda/MRI_ROOT/rawdata/sub-YA01508/ses-202206231',
        '-dwipreproc',
        ])
        # '-mriqc', '-fmriprep', '-dwipreproc',

    print(args)
    dicom_to_bids_QQC(args)


def test_sept_GE():
    args = parse_args([
        '-i', '/data/predict/phantom_data/kcho/GE_experiment/GE_Sept/dicoms',
        '-s', 'GE',
        '-ss', 'sept',
        '-o', '/data/predict/phantom_data/kcho/GE_experiment/GE_Sept/BIDS',
        '-std', '/data/predict/data_from_nda_dev/MRI_ROOT/rawdata/sub-AD00001/ses-202109061',
        ])
        # '-mriqc', '-fmriprep', '-dwipreproc',

    print(args)
    dicom_to_bids_QQC(args)


def test_prev_calgary():
    args = parse_args([
        '-i', '/data/predict/phantom_human_pilot/sourcedata/ProNET_Calgary_GE/ses-humanpilot',
        '-s', 'GE',
        '-ss', 'calgary',
        '-o', '/data/predict/phantom_data/kcho/GE_experiment/GE_Sept/BIDS',
        '-std', '/data/predict/data_from_nda_dev/MRI_ROOT/rawdata/sub-AD00001/ses-202109061',
        ])
        # '-mriqc', '-fmriprep', '-dwipreproc',

    print(args)
    dicom_to_bids_QQC(args)


def test_prev_calgary_phantom():
    args = parse_args([
        '-i', '/data/predict/phantom_human_pilot/sourcedata/ProNET_Calgary_GE/ses-phantom',
        '-s', 'GE',
        '-ss', 'calgary_phantom',
        '-o', '/data/predict/phantom_data/kcho/GE_experiment/GE_Sept/BIDS',
        '-std', '/data/predict/data_from_nda_dev/MRI_ROOT/rawdata/sub-AD00001/ses-202109061',
        ])
        # '-mriqc', '-fmriprep', '-dwipreproc',

    print(args)
    dicom_to_bids_QQC(args)
