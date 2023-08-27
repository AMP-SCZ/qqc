import re
import sys
import logging
import zipfile
import tempfile
import os
import pandas as pd
import shutil
import configparser
from pathlib import Path
from typing import List, Tuple
from qqc.run_sheet import get_run_sheet, get_matching_run_sheet_path
from qqc.dicom_files import get_dicom_files_walk, rearange_dicoms, \
        get_dicom_counts, update_dicom_counts
from qqc.heudiconv_ctrl import run_heudiconv
from qqc.qqc.json import jsons_from_bids_to_df
from qqc.qqc.dicom import check_num_order_of_series, save_csa, is_enhanced, \
        is_xa30
from qqc.qqc.json import within_phantom_qc, compare_data_to_standard
from qqc.qqc.qqc_summary import qqc_summary, qqc_summary_for_dpdash, \
        refresh_qqc_summary_for_subject
from qqc.qqc.figures import quick_figures
from qqc.qqc.mriqc import run_mriqc_on_data
from qqc.qqc.fmriprep import run_fmriprep_on_data
from qqc.qqc.dwipreproc import run_quick_dwi_preproc_on_data
from qqc.email import send_out_qqc_results, send_error, \
        extract_info_for_qqc_report
import getpass
from datetime import datetime, date, timedelta
from jinja2 import Environment, FileSystemLoader
from qqc.email import create_html_for_qqc, create_html_for_qqc_study

pd.set_option('max_columns', 50)
pd.set_option('max_rows', 500)
logger = logging.getLogger(__name__)
logging.getLogger().addHandler(logging.StreamHandler())


def dicom_to_bids_QQC(args, **kwargs) -> None:
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
    debug = kwargs.get('debug', False)
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
        if args.input is None:
            qqc_input = Path(args.nifti_dir)
            dicom_count_input_df = pd.DataFrame()
        else:
            qqc_input = Path(args.input)
        # For BIDS format, session name cannot have "-" or "_"
        session_name = 'ses-' + re.sub('[_-]', '', args.session_name)

        # For BIDS format, subject name cannot have "-" or "_"
        subject_name = 'sub-' + re.sub('[_-]', '', args.subject_name)
        # find the matching run sheet
        run_sheet = get_matching_run_sheet_path(qqc_input, args.session_name)
            
    site = args.subject_name[:2]
    raw_input_given = qqc_input

    # str variables to Path
    bids_root = Path(args.bids_root)
    deriv_p = bids_root / 'derivatives'
    if args.qc_subdir:
        qc_out_dir = Path(args.qc_subdir)
    else:
        qc_out_dir = deriv_p / 'quick_qc' / subject_name / session_name
    qc_out_dir.mkdir(exist_ok=True, parents=True)

    # BIDS_root / rawdata / sub-${subject} / ses-${session}
    subject_dir = bids_root / 'rawdata' / subject_name
    session_dir = subject_dir / session_name  # raw nifti path

    # raw dicom -> cleaned up dicom structure
    dicom_clearned_up_output = bids_root / 'sourcedata'
    sorted_dicom_dir = dicom_clearned_up_output / \
                      subject_name.split('-')[1] / \
                      ('ses-' + session_name.split('-')[1])


    # ----------------------------------------------------------------------
    # Copy the data
    # ----------------------------------------------------------------------
    # if the input is a zip file, decompress it to a temporary directory
    if qqc_input.name.endswith('.zip') or qqc_input.name.endswith('.ZIP'):
        # if there are XA30 t1w dir
        qqc_input = unzip_and_update_input(qqc_input,
                                           sorted_dicom_dir,
                                           args.force_copy_dicom_to_source)

    # XA30
    logger.info(f'Site : {site}')
    standard_dir = None
    if args.standard_dir is None:
        config = configparser.ConfigParser()
        config.read(args.config)
        for root, dirs, files in os.walk(qqc_input):
            for subdir in dirs:
                if is_xa30(qqc_input):
                    try:
                        standard_dir = Path(config.get('XA30 template', site))
                    except KeyError:
                        standard_dir = Path(config.get('XA30 template', 'ME'))
                    logger.info(f'XA 30 template: {standard_dir}')

                    if is_enhanced(qqc_input):
                        try:
                            standard_dir = Path(config.get(
                                'XA30 template enhanced', site))
                        except KeyError:
                            standard_dir = Path(config.get('XA30 template',
                                                           'ME'))
                        logger.info(f'XA 30 ehanced template: {standard_dir}')
                    break
            break
                # elif '!' in subdir.lower():
                    # # sys.exit()  # GE data  #TODO
                    # standard_dir = Path(config.get('GE template', 'a'))
                    # break

        if standard_dir is None:
            try:
                standard_dir = Path(config.get('First Scan', site))
            except configparser.NoOptionError:
                logger.critical(f'{site} is not in the First Scan')
                logger.critical('Setting the template as YA')
                standard_dir = Path(config.get('First Scan', 'YA'))
            except KeyError:
                standard_dir = Path(config.get('First Scan', 'YA'))
    else:
        standard_dir = Path(args.standard_dir)

    if args.nifti_dir:  # if nifti directory is given
        df_full = get_information_from_rawdata(args.nifti_dir)
        session_dir = Path(args.nifti_dir)  # update session_dir
    else:  # if the input given is a dicom directory or dicom zip
        # raw dicom counts
        logger.info('Running dicom_to_bids to sort and convert dicom files')
        if 'CP' in subject_name:
            message = 'Overwritten quick_scan to False, since Philips data'
            logger.info(message)
            args.quick_scan = False

        df_full = get_dicom_df(qqc_input,
                               args.skip_dicom_rearrange,
                               sorted_dicom_dir,
                               args.quick_scan)

        logger.info('Arranging dicoms')

        if not args.skip_dicom_rearrange:
            if 'CP' in subject_name or 'GW' in subject_name:
                args.rename_dicoms = True

            rearange_dicoms(df_full, dicom_clearned_up_output,
                            subject_name.split('-')[1],
                            session_name.split('-')[1],
                            force=args.force_copy_dicom_to_source,
                            rename_dicoms=args.rename_dicoms)

            df_full = get_dicom_df(sorted_dicom_dir,
                                   True,
                                   sorted_dicom_dir,
                                   True)


        dicom_count_input_df = get_dicom_counts(Path(sorted_dicom_dir),
                                                debug=debug)

        # cleaned up dicom structure -> BIDS
        bids_rawdata_dir = bids_root / 'rawdata'
        if not args.skip_heudiconv:
            logger.info('Get dicom counts')
            logger.info('Run heudiconv')
            qc_out_dir.mkdir(exist_ok=True, parents=True)

            heudiconv_nifti_dir_out = bids_rawdata_dir / subject_name / \
                    session_name

            # if heudiconv_nifti_dir_out.is_dir():
                # if len(list(heudiconv_nifti_dir_out.glob('*'))) > 0:
                    # pass
                # else:
                    # run_heudiconv(dicom_clearned_up_output,
                                  # subject_name.split('-')[1],
                                  # session_name.split('-')[1],
                                  # bids_rawdata_dir,
                                  # qc_out_dir,
                                  # args.force_heudiconv)
            # else:
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

        # update dicom_count_input_df
        dicom_count_input_df = update_dicom_counts(dicom_count_input_df,
                                                   session_dir,
                                                   debug=debug)
        dicom_count_input_df.to_csv(qc_out_dir / 'dicom_count.csv')

    # run sheet
    if run_sheet.is_file():
        run_sheet_df = get_run_sheet(run_sheet)
    else:
        logger.warning(f'Run sheet not found: {run_sheet}')
        run_sheet_df = pd.DataFrame()

    # ----------------------------------------------------------------------
    # Run QQC
    # ----------------------------------------------------------------------
    if not args.skip_qc:
        # try:
        run_qqc(qc_out_dir, session_dir, df_full, standard_dir)
        # except:
            # save_qqc_error(qc_out_dir)

        sender, recipients, title, subtitle, top_message, qc_detail, \
                    code, image_paths, qqc_html_list, in_mail_footer = \
            extract_info_for_qqc_report(raw_input_given, qc_out_dir,
                                        standard_dir, run_sheet_df,
                                        dicom_count_input_df)
                                        
        admin_recipient = 'kc244@research.partners.org'
        user_id = getpass.getuser()
        recipients = list(set(
            [f'{user_id}@research.partners.org'] + args.additional_recipients))

        # get template
        env = Environment(loader=FileSystemLoader(str(
            os.path.join(os.path.dirname(__file__), 'email'))))

        # html form to be used for email
        email_template = env.get_template('bootdey_template_clean.html')
        html_str = create_html_for_qqc(email_template, title, subtitle,
                top_message, qc_detail, code, in_mail_footer,
                image_paths)

        # html form to be saved in the server
        template = env.get_template('bootdey_template.html')
        html_str = create_html_for_qqc(
                template, title, subtitle,
                top_message, qc_detail, code, in_mail_footer,
                image_paths)
        outloc = Path(qc_out_dir) / 'qqc_summary.html'
        with open(outloc, 'w') as fh:
            fh.write(html_str)

        # study level html
        study_template = env.get_template('bootdey_template_study.html')
        study_level_html = Path(qc_out_dir).parent.parent / 'study_summary.html'
        study_level_csv = Path(qc_out_dir).parent.parent / 'study_summary.csv'

        title = 'QQC report summary'
        subtitle = f'Created on {date.today().strftime("%m/%d/%y")}'
        first_message = qc_out_dir.parent.parent.parent.parent
        second_message = ''

        # save as csv file
        pd.DataFrame(qqc_html_list).to_csv(study_level_csv)

        html_str = create_html_for_qqc_study(study_template,
                title, subtitle,
                first_message, second_message, code, in_mail_footer,
                qqc_html_list)
        with open(study_level_html, 'w') as fh:
            fh.write(html_str)

    # ----------------------------------------------------------------------
    # Email
    # ----------------------------------------------------------------------
    if args.email_report:
        logger.info('Sending out email')
        send_out_qqc_results(raw_input_given, qc_out_dir, standard_dir,
                             run_sheet_df, args.additional_recipients,
                             dicom_count_input_df)

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
            dwipreproc_outdir_root,
            bsub=True)

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
            logger.warning(f'There are more than {num} {series_desc}')
            df_tmp = df_unique_series[
                df_unique_series.series_desc == series_desc]
            logger.info(df_tmp.sort_values('series_num'))

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

    if should_break:
        sys.exit()

    return df_full


def get_dicom_df(dicom_input_dir: Path,
                 skip_dicom_rearrange: bool = False,
                 sorted_dicom_dir: Path = None,
                 quick_scan: bool = False) -> pd.DataFrame:
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
        if Path(sorted_dicom_dir).is_dir():
            df_full = get_dicom_files_walk(sorted_dicom_dir, True)
        else:
            df_full = get_dicom_files_walk(dicom_input_dir, True)
    elif quick_scan:
        logger.info('Copy and rearrange dicoms')
        logger.info('assuming single series in a directory')
        df_full = get_dicom_files_walk(dicom_input_dir, quick_scan=quick_scan)
    else:
        logger.info('Copy and rearrange dicoms')
        df_full = get_dicom_files_walk(dicom_input_dir)

        # remove repeated scans
        # df_full = remove_repeated_scans(df_full)


    # ignore FA and colFA maps
    df_full = df_full[~df_full['series_desc'].str.contains(
            '_fa', flags=re.IGNORECASE, regex=True)]
    df_full = df_full[~df_full['series_desc'].str.contains(
            '_colfa', flags=re.IGNORECASE, regex=True)]
    df_full = df_full[~df_full['series_desc'].str.contains(
            'phoenixzipreport', flags=re.IGNORECASE, regex=True)]

    return df_full


def unzip_and_update_input(input: str,
                           sorted_dicom_dir: Path,
                           force: bool = False) -> str:
    '''Unzip the MRI files to a temporary dir and return the path'''
    logger.info('See if there is already re-arranged dicom files')
    if not force:
        dicom_dirs = [x for x in sorted_dicom_dir.glob('*') if x.is_dir()]
        if len(dicom_dirs) > 4:
            return sorted_dicom_dir

    logger.info('Input is a zip file. Extracting it to a temp directory')
    zf = zipfile.ZipFile(input)
    tf = tempfile.mkdtemp(
            prefix=(Path(input).stem + '_'),
            dir='/data/predict1/home/kcho/tmp/zip_tempdir')
    zf.extractall(tf)

    return tf


def get_matching_standard_dir(qqc_input: Path) -> Path:
    '''Read configuration file and return matching standard dir'''
    pass


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
    try:
        save_csa(df_with_one_series, qc_out_dir, standard_dir)
    except KeyError:
        logger.warning('No pydicom information in df_with_one_series')
    except ValueError:
        logger.warning('No pydicom information in df_with_one_series')

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


def save_qqc_error(qqc_out_dir: Path) -> None:
    '''Save QQC error to be visualized in the Study page

    Key Argument
        qc_out_dir: QQC output path, Path.
        nifti_session_dir: nifti data path, Path.
        df_full: series information, pd.DataFrame.
        standard_dir: nifti data path of the template session, Path.
        run_sheet_df: MRI run sheet information, pd.DataFrame

    Returns:
        None
    '''
    session_name = qqc_out_dir.name.split('-')[1]
    subject_name = qqc_out_dir.parent.name.split('-')[1]

    title = f'{subject_name} - MRI QQC'
    subtitle = 'Automatically created message ' \
               f'for {subject_name} ({session_name})'
    qqc_html_file = qqc_out_dir / 'qqc_summary.html'
    env = Environment(loader=FileSystemLoader(str(
        os.path.join(os.path.dirname(__file__), 'email'))))
    # html form to be used for email
    email_template = env.get_template('bootdey_template_clean.html')

    str_tmp = '<h4>{0} </h4><code>{1}</code><br><br>'
    in_mail_footer = str_tmp.format('QQC ran on', datetime.now().date())
    in_mail_footer += str_tmp.format('QQC ran by', getpass.getuser())

    html_str = create_html_for_qqc(email_template, title, subtitle,
            'QQC failed', 'QQC failed', [''], in_mail_footer, [])
