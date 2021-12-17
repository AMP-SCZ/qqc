#!/data/pnl/kcho/anaconda3/bin/python
import argparse
import sys
import re
import getpass
import logging
from pathlib import Path
import pandas as pd
from typing import List, Tuple
from argparse import RawTextHelpFormatter

from phantom_check.dicom_files import get_dicom_files_walk, \
        rearange_dicoms
from phantom_check.heudiconv_ctrl import run_heudiconv
from phantom_check.qqc.json import jsons_from_bids_to_df
from phantom_check.qqc.dicom import check_num_order_of_series, save_csa
from phantom_check.qqc.json import within_phantom_qc, \
        compare_data_to_standard, compare_data_to_standard_lazy
from phantom_check.qqc.figures import quick_figures

pd.set_option('max_columns', 50)
pd.set_option('max_rows', 500)

logger = logging.getLogger(__name__)
logging.getLogger().addHandler(logging.StreamHandler())



def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
        description='''Convert dicoms to BIDS

    dicom_to_dpacc_bids.py \\
        --input_dir ${raw_dicom_dir}/human_pilot/data/dicom \\
        --subject_name Pronet_PNL \\
        --session_name humanpilot \\
        --output_dir ${bids_out_dir} \\
        --standard_dir ${bids_out_dir}/rawdata/sub-standard/ses-humanpilot''',
        formatter_class=RawTextHelpFormatter)

    # image input related options
    parser.add_argument('--input_dir', '-i', type=str,
                        help='Raw dicom root directory.')

    parser.add_argument('--subject_name', '-s', type=str,
                        help='Subject name.')

    parser.add_argument('--session_name', '-ss', type=str,
                        help='Session name.')

    parser.add_argument('--output_dir', '-o', type=str,
                        help='BIDS Output directory')

    parser.add_argument('--standard_dir', '-std', type=str,
                        help='Root of a standard dataset to compare to')

    parser.add_argument('--skyra', '-sk', action='store_true',
                        help='For skyra scans - match DWI / compared to other '
                             'skyra etc. (Option for U24 study)')

    parser.add_argument('--nifti_dir', '-nd', type=str, default=False,
                        help='Nifti root directory. If --nifti_dir is given, '
                             '--input_dir will be ignored and dcm2niix will '
                             'not be ran.')

    parser.add_argument('--partial_rescan', '-ps', action='store_true',
                        help='Use series name to find matching serieses - '
                             'Maybe useful for partial rescan')

    # extra options
    args = parser.parse_args(argv)
    return args


def dicom_to_bids_with_quick_qc(args) -> None:
    '''Sort dicoms, convert to BIDS nifti structure and run quick QC.

    Key arguments:
        args: Argparse parsed arguments.
            - Must have following attributes
              - subject_name: name of the subject, str.
              - session_name: name of the session, str.
              - input_dir: raw dicom root directory, str.
              - output_dir: output BIDS raw directory, str.

            - Optional attributes
              - standard_dir: root of a standard dataset to compare the input
                              data to, str.
              - nifti_dir: if the input_dir is BIDS nifti directory, bool.
              - skyra: if the input_dir is skyra data, bool.

    Returns:
        None

    Notes:
        1. run dicom to dicom BIDS
    '''
    logger.info('Setting up subject, session, and output variables')

    # session name cannot have "-" or "_"
    args.session_name = re.sub('[_-]', '', args.session_name)

    # subject_dir
    # BIDS_root / rawdata / sub-${subject} / ses-${session}
    subject_dir = Path(args.output_dir) / 'rawdata' / \
        ('sub-' + re.sub('[_-]', '', args.subject_name))
    session_dir = subject_dir / ('ses-' + args.session_name)

    # QC output
    # BIDS_root / derivatives / quick_qc
    qc_out_dir = Path(args.output_dir) / 'derivatives' / 'quick_qc' / \
        subject_dir.name / session_dir.name

    try:
        qc_out_dir.mkdir(exist_ok=True, parents=True)
    except PermissionError:
        logger.critical("No permission to write under %s" % qc_out_dir.parent)


    # Raw dicom to ordered Dicom then to BIDS
    if args.nifti_dir:  # if nifti directory is given
        logger.info('Loading user provided Nifti directory to load JSON files')
        session_dir = args.nifti_dir
        try:
            assert Path(args.nifti_dir).is_dir(), \
                    'The Nifti directory does not exist'
        except AssertionError:
            logger.critical(
                'User provided Nifti directory does not exist: %s' %
                args.nifti_dir)
        df_full = jsons_from_bids_to_df(args.nifti_dir)

    else:  # if the input_dir given is a dicom directory
        logger.info('Running dicom_to_bids to sort and convert dicom files')

        # raw dicom -> cleaned up dicom structure
        df_full = get_dicom_files_walk(args.input_dir)
        dicom_clearned_up_output = Path(args.output_dir) / 'sourcedata'
        rearange_dicoms(df_full, dicom_clearned_up_output,
                        args.subject_name, args.session_name)

        # cleaned up dicom structure -> BIDS
        nifti_dir = Path(args.output_dir) / 'rawdata'
        run_heudiconv(dicom_clearned_up_output, args.subject_name,
                      args.session_name, nifti_dir)


    # args.partial_rescan: True if serieses need to be reordered by their
    # description, bool.
    # if args.partial_rescan:
        # logger.info('Partial scan option is used. '
                    # 'Changing series number to match target series number')
        # if args.skyra:
            # series_num_target_dict = {
                # 1:'Localizer',
                # 2:'AAHScout',
                # 3:'AAHScout_MPR_sag',
                # 4:'AAHScout_MPR_cor',
                # 5:'AAHScout_MPR_tra',
                # 6:'Localizer_aligned',
                # 7:'DistortionMap_AP',
                # 8:'DistortionMap_PA',
                # 9:'T1w_MPR',
                # 10:'T1w_MPR',
                # 11:'T2w_SPC',
                # 12:'T2w_SPC',
                # 13:'DistortionMap_AP',
                # 14:'DistortionMap_PA',
                # 15:'rfMRI_REST_AP_SBRef',
                # 16:'rfMRI_REST_AP',
                # 17:'rfMRI_REST_PA_SBRef',
                # 18:'rfMRI_REST_PA',
                # 19:'dMRI_b0_AP_SBRef',
                # 20:'dMRI_b0_AP',
                # 21:'dMRI_dir126_PA_SBRef',
                # 22:'dMRI_dir126_PA',
                # 23:'dMRI_b0_AP_SBRef',
                # 24:'dMRI_b0_AP',
                # 25:'DistortionMap_AP',
                # 26:'DistortionMap_PA',
                # 27:'rfMRI_REST_AP_SBRef',
                # 28:'rfMRI_REST_AP',
                # 29:'rfMRI_REST_PA_SBRef',
                # 30:'rfMRI_REST_PA'}
        # else:
            # series_num_target_dict = {
                # 1:'Localizer',
                # 2:'AAHScout',
                # 3:'AAHScout_MPR_sag',
                # 4:'AAHScout_MPR_cor',
                # 5:'AAHScout_MPR_tra',
                # 6:'Localizer_aligned',
                # 7:'DistortionMap_AP',
                # 8:'DistortionMap_PA',
                # 9:'T1w_MPR',
                # 10:'T1w_MPR',
                # 11:'T2w_SPC',
                # 12:'T2w_SPC',
                # 13:'DistortionMap_AP',
                # 14:'DistortionMap_PA',
                # 15:'rfMRI_REST_AP_SBRef',
                # 16:'rfMRI_REST_AP',
                # 17:'rfMRI_REST_PA_SBRef',
                # 18:'rfMRI_REST_PA',
                # 19:'dMRI_b0_AP_SBRef',
                # 20:'dMRI_b0_AP',
                # 21:'dMRI_dir176_PA_SBRef',
                # 22:'dMRI_dir176_PA',
                # 23:'dMRI_b0_AP_SBRef',
                # 24:'dMRI_b0_AP',
                # 25:'DistortionMap_AP',
                # 26:'DistortionMap_PA',
                # 27:'rfMRI_REST_AP_SBRef',
                # 28:'rfMRI_REST_AP',
                # 29:'rfMRI_REST_PA_SBRef',
                # 30:'rfMRI_REST_PA'}

        # series_num_target_dict = {y: x for x, y in
                # series_num_target_dict.items()}

        # df_full['orig_series_num'] = df_full['series_num']
        # df_full['series_num'] = df_full['series_desc'].map(
                # series_num_target_dict)


    logger.info('Checking number and order of scan series')
    # check number & order of series
    print('Check number & order of series')
    check_num_order_of_series(df_full, qc_out_dir, args.skyra)

    # within data QC
    logger.info('Beginning within scan QC')
    print('Within phantom QC')
    within_phantom_qc(session_dir, qc_out_dir)

    # CSA extraction
    print('CSA extraction')
    df_with_one_series = pd.concat([
        x[1].iloc[0] for x in df_full.groupby('series_num')], axis=1).T
    save_csa(df_with_one_series, qc_out_dir)

    if args.standard_dir:
        print('Comparison to standard')
        compare_data_to_standard(session_dir, args.standard_dir,
                                 qc_out_dir, args.partial_rescan)

        # skyra scans have different number of diffusion weighting,
        # therefore, need to compare DWI manually
        if args.skyra:
            compare_data_to_standard_lazy(
                    session_dir, args.standard_dir, qc_out_dir,
                    args.partial_rescan)


    if args.skyra:
        skyra_preset_loc = '/data/predict/phantom_human_pilot/rawdata/' \
                           'sub-PrescientAdelaideSkyra/ses-humanpilot'
        print('Comparison to Skyra standard')
        print(f'Preset to {skyra_preset_loc}')
        qc_out_dir_skyra = qc_out_dir / 'comparison_to_skyra_Adelaide'
        qc_out_dir_skyra.mkdir(exist_ok=True, parents=True)
        compare_data_to_standard(
                session_dir, skyra_preset_loc, qc_out_dir_skyra,
                args.partial_rescan)

    print('Creating summary figures')

    try:
        quick_figures(session_dir, qc_out_dir)
    except RuntimeError:
        print('Error in creating figures')


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    logging.basicConfig(
            filename=args.output_dir + '/dicom_to_dpacc_bids.log',
            format=f'%(asctime):: {getpass.getuser()}:: %(name)s :: '
                   '%(levelname)s :: %(message)s',
            datefmt = '%Y-%m-%d %H:%M:%S',
            level=logging.DEBUG)


    # build up input command to include in the log
    logger.info('*'*80)
    args_reconstruct = ''
    for d in [x for x in dir(args) if not x.startswith('_')]:
        args_reconstruct += f' --{d}={getattr(args, d)}'
    logger.info(f'command used: \ndicom_to_dpacc_bids.py {args_reconstruct}')

    logger.info('Dicom to DPACC BIDS conversion started')
    dicom_to_bids_with_quick_qc(args)
    logger.info('Completed')

