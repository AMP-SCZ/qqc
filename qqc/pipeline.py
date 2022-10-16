import re
import sys
import logging
import zipfile
import tempfile
import pandas as pd
import shutil
from pathlib import Path
from typing import List, Tuple
from qqc.run_sheet import get_run_sheet, get_matching_run_sheet_path
from qqc.dicom_files import get_dicom_files_walk, rearange_dicoms
from qqc.heudiconv_ctrl import run_heudiconv
from qqc.qqc.json import jsons_from_bids_to_df
from qqc.qqc.dicom import check_num_order_of_series, save_csa
from qqc.qqc.json import within_phantom_qc, compare_data_to_standard
from qqc.qqc.qqc_summary import qqc_summary, qqc_summary_for_dpdash, \
        refresh_qqc_summary_for_subject
from qqc.qqc.figures import quick_figures
from qqc.qqc.mriqc import run_mriqc_on_data
from qqc.qqc.fmriprep import run_fmriprep_on_data
from qqc.qqc.dwipreproc import run_quick_dwi_preproc_on_data
from qqc.email import send_out_qqc_results, send_error

pd.set_option('max_columns', 50)
pd.set_option('max_rows', 500)
logger = logging.getLogger(__name__)
logging.getLogger().addHandler(logging.StreamHandler())


def dicom_to_bids_QQC(args) -> None:
    '''Sort dicoms, convert to BIDS nifti structure and run quick QC.

    Key arguments:
        args: Argparse parsed arguments. It must have following attributes.
          - subject_name: name of the subject, str.
          - session_name: name of the session, str.
          - input: raw dicom root directory, str.
          - bids_root: output BIDS raw directory, str.

        - Optional attributes
          - standard_dir: root of a standard dataset to compare the input
                          data to, str.
          - nifti_dir: if the input is BIDS nifti directory, bool.

    Returns:
        None

    Notes:
        1. Sort dicoms according to a clean structure.
        2. Run heudiconv to convert dicoms into nifti files in BIDS format.
        3. Run QQC (Quick-QC)
    '''
    logger.info('Setting up subject, session, and output variables')

    # ----------------------------------------------------------------------
    # Variable settings
    # ----------------------------------------------------------------------
    if args.dpacc_input:
        qqc_input = Path(args.dpacc_input)
        session_name = args.input.name
        subject_name = args.input.parent.parent.name
        bids_root = Path('/data/predict/kcho/flow_test/MRI_ROOT')
        run_sheet = next(args.input.parent.glob('*Run_sheet_mri*.csv'))
    else:
        qqc_input = Path(args.input)
        # For BIDS format, session name cannot have "-" or "_"
        session_name = 'ses-' + re.sub('[_-]', '', args.session_name)

        # For BIDS format, subject name cannot have "-" or "_"
        subject_name = 'sub-' + re.sub('[_-]', '', args.subject_name)

        # find the matching run sheet
        run_sheet = get_matching_run_sheet_path(args.input, args.session_name)
            
    # str variables to Path
    bids_root = Path(args.bids_root)
    deriv_p = bids_root / 'derivatives'
    if args.qc_subdir:
        qc_out_dir = Path(args.qc_subdir)
    else:
        qc_out_dir = deriv_p / 'quick_qc' / subject_name / session_name
    qc_out_dir.mkdir(exist_ok=True, parents=True)
    standard_dir = Path(args.standard_dir)
    # BIDS_root / rawdata / sub-${subject} / ses-${session}
    subject_dir = bids_root / 'rawdata' / subject_name
    session_dir = subject_dir / session_name  # raw nifti path

    # ----------------------------------------------------------------------
    # Copy the data
    # ----------------------------------------------------------------------
    # if the input is a zip file, decompress it to a temporary directory
    if qqc_input.name.endswith('.zip') or qqc_input.name.endswith('.ZIP'):
        qqc_input = unzip_and_update_input(qqc_input)

    if args.nifti_dir:  # if nifti directory is given
        df_full = get_information_from_rawdata(args.nifti_dir)
        session_dir = Path(args.nifti_dir)  # update session_dir
    else:  # if the input given is a dicom directory or dicom zip
        logger.info('Running dicom_to_bids to sort and convert dicom files')

        # raw dicom -> cleaned up dicom structure
        dicom_clearned_up_output = bids_root / 'sourcedata'
        df_full = get_dicom_df(qqc_input, args.skip_dicom_rearrange)

        logger.info('Arranging dicoms')
        rearange_dicoms(df_full, dicom_clearned_up_output,
                        subject_name.split('-')[1],
                        session_name.split('-')[1],
                        args.force_copy_dicom_to_source)

        # cleaned up dicom structure -> BIDS
        bids_rawdata_dir = bids_root / 'rawdata'
        if not args.skip_heudiconv:
            logger.info('Run heudiconv')
            qc_out_dir.mkdir(exist_ok=True, parents=True)
            run_heudiconv(dicom_clearned_up_output,
                          subject_name.split('-')[1],
                          session_name.split('-')[1],
                          bids_rawdata_dir,
                          qc_out_dir,
                          args.force_heudiconv)

            # remove temporary directory
            if Path(qqc_input).name.endswith('.zip') or \
                    Path(qqc_input).name.endswith('.ZIP'):
                shutil.rmtree(qqc_input)

    # run sheet
    if run_sheet.is_file():
        run_sheet_df = get_run_sheet(run_sheet)
    else:
        print(f'Run sheet not found: {run_sheet}')
        run_sheet_df = pd.DataFrame()

    # ----------------------------------------------------------------------
    # Run QQC
    # ----------------------------------------------------------------------
    if not args.skip_qc:
        run_qqc(qc_out_dir, session_dir, df_full, standard_dir)

    # ----------------------------------------------------------------------
    # Email
    # ----------------------------------------------------------------------
    if args.standard_dir:
        logger.info('Sending out email')
        send_out_qqc_results(qc_out_dir, standard_dir,
                             run_sheet_df, args.additional_recipients)

    # ----------------------------------------------------------------------
    # AMPSCZ pipeline
    # ----------------------------------------------------------------------
    if args.dwipreproc:
        # quick dwi preprocessing
        dwipreproc_outdir_root = deriv_p / 'dwipreproc'
        run_quick_dwi_preproc_on_data(
            bids_root / 'rawdata',
            subject_dir.name,
            session_dir.name,
            dwipreproc_outdir_root)

    if args.mriqc:
        # mriqc
        mriqc_outdir_root = deriv_p / 'mriqc'
        run_mriqc_on_data(
            bids_root / 'rawdata',
            subject_dir.name,
            session_dir.name,
            mriqc_outdir_root)

    if args.fmriprep:
        # fmriprep
        fmriprep_outdir_root = deriv_p / 'fmriprep'
        fs_outdir_root = deriv_p / 'freesurfer'
        run_fmriprep_on_data(
            bids_root / 'rawdata',
            subject_dir.name,
            session_dir.name,
            fmriprep_outdir_root,
            fs_outdir_root)

    # ----------------------------------------------------------------------
    # Run Figure extraction
    # ----------------------------------------------------------------------
    logger.info('Creating summary figures')
    if not args.qc_subdir:
        try:
            quick_figures(session_dir, qc_out_dir)
        except RuntimeError:
            logger.info('Error in creating figures')
        except OSError:
            logger.info('OSError in creating figures')



def get_information_from_rawdata(nifti_dir: Path):
    logger.info('Loading user provided Nifti directory to load JSON files')
    nifti_dir = Path(nifti_dir)
    assert nifti_dir.is_dir(), 'The Nifti directory does not exist'
    df_full = jsons_from_bids_to_df(nifti_dir)

    return df_full


def remove_repeated_scans(df_full: pd.DataFrame) -> pd.DataFrame:
    '''Remove repeated scans, which may raise error with our heuristic files'''
    # check if there is any re-scanned series in the inputs
    df_unique_series = df_full[['series_desc', 'series_num']
        ].drop_duplicates().reset_index(
            drop=True).sort_values('series_num')

    distortion_index = df_unique_series[
        df_unique_series.series_desc.str.contains(
            'distortion', flags=re.IGNORECASE)].index

    for index, row in df_unique_series.loc[
            distortion_index].iterrows():
        range_of_index = range(index, df_unique_series.index[-1])
        for _, matching_row in df_unique_series.loc[
                list(range_of_index)].iterrows():
            if 'distortion' not in matching_row.series_desc.lower():
                df_unique_series.loc[index,
                                     'distortion_map_before'] = \
                                             matching_row.series_desc
                break

    series_desc_num_dict = {'T1w_MPR': 2,
                            'T2w_SPC': 2,
                            'DistortionMap_AP':3,
                            'DistortionMap_PA':3}

    should_break = False
    df_full_excluded = []

    # TODO
    if len(series_desc_num_dict) > 0:
        # send_error(f'QQC - repeated scans {subject_name} {session_name}',
        send_error(f'QQC - repeated scans ',
                   'There are repated scans. Please double check manually',
                   'Number of each series',
                   pd.DataFrame(series_desc_num_dict).to_html())

    for series_desc, num in series_desc_num_dict.items():
        if len(df_unique_series[
                df_unique_series.series_desc == series_desc]) > num:
            print(f'There are more than {num} {series_desc}')
            df_tmp = df_unique_series[
                df_unique_series.series_desc == series_desc]
            print(df_tmp.sort_values('series_num'))

            choose = input('Raw to remove (index, separated by space): ')
            choose_list = [int(x) for x in choose.split(' ')]
            for choose in choose_list:
                if choose in df_tmp.index:
                    df_full_excluded.append(df_full[
                        df_full.series_num == df_tmp.loc[choose]['series_num']
                        ])
                    df_full = df_full[
                        df_full.series_num != df_tmp.loc[choose][
                            'series_num']]
                else:
                    should_break = True
            print()

    if should_break:
        sys.exit()

    return df_full


def get_dicom_df(dicom_input_dir: Path,
                 skip_dicom_rearrange: bool = False) -> pd.DataFrame:
    '''Rearrange dicoms and load series information after removing extra scans

    Runs:
        - get_dicom_files_walk
        - remove_repeated_scans

    Key arguments:
        dicom_input_dir: dicom input path, Path
        skip_dicom_rearrange: True if don't need dicom rearrange, bool

    Returns:
        pd.dataframe
    '''
    logger.info('Running dicom_to_bids to sort and convert dicom files')

    if skip_dicom_rearrange:
        logger.info('Skip dicom rearrange')
        df_full = get_dicom_files_walk(dicom_input_dir, True)
    else:
        logger.info('Copy and rearrange dicoms')
        df_full = get_dicom_files_walk(dicom_input_dir)

        # remove repeated scans
        # df_full = remove_repeated_scans(df_full)

    return df_full


def unzip_and_update_input(input: str) -> str:
    '''Unzip the MRI files to a temporary dir and return the path'''
    logger.info('Input is a zip file. Extracting it to a temp directory')
    zf = zipfile.ZipFile(input)
    tf = tempfile.mkdtemp(
            prefix='/data/predict/kcho/tmp/zip_tempdir/')
    zf.extractall(tf)

    return tf


def run_qqc(qc_out_dir: Path, nifti_session_dir: Path,
            df_full: pd.DataFrame, standard_dir: Path) -> None:
    '''Run QQC

    Key Argument
        qc_out_dir: QQC output path, Path.
        nifti_session_dir: nifti data path, Path.
        df_full: series information, pd.DataFrame.
        standard_dir: nifti data path of the template session, Path.
        run_sheet_df: MRI run sheet information, pd.DataFrame

    Returns:
        None
    '''
    # within data QC
    logger.info('Beginning within scan QC')
    within_phantom_qc(nifti_session_dir, qc_out_dir)

    logger.info('CSA extraction')
    df_with_one_series = pd.concat(
        [x[1].iloc[0] for x in df_full.groupby('series_num')],
        axis=1).T
    save_csa(df_with_one_series, qc_out_dir, standard_dir)

    # load json information from the user givin standard BIDS directory
    df_full_std = jsons_from_bids_to_df(standard_dir).drop_duplicates()
    df_full_std.sort_values('series_num', inplace=True)

    logger.info('Checking number and order of scan series')
    df_full['series_desc'] = df_full['series_desc'].str.lower()
    df_full_std['series_desc'] = df_full_std['series_desc'].str.lower()
    check_num_order_of_series(df_full, df_full_std, qc_out_dir)

    logger.info('Comparison to standard')
    compare_data_to_standard(nifti_session_dir, standard_dir, qc_out_dir)

    logger.info('Summary function & DPdash')
    # qqc_summary_for_dpdash(qc_out_dir)
    try:
        # this requires formsqc to be processed
        refresh_qqc_summary_for_subject(qc_out_dir.parent)
    except:
        pass
