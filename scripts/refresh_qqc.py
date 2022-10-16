from qqc.qqc.qqc_summary import qqc_summary_for_dpdash, \
        refresh_qqc_summary_for_subject
import re
from qqc.qqc.mriqc import run_mriqc_on_data
from qqc.dicom_files import get_dicom_files_walk
from qqc.qqc.dwipreproc import run_quick_dwi_preproc_on_data
from pathlib import Path
from qqc.qqc.dicom import check_num_order_of_series, save_csa
from qqc.qqc.json import jsons_from_bids_to_df
import pandas as pd
import argparse
import sys
from argparse import RawTextHelpFormatter
from qqc.qqc.json import within_phantom_qc, \
        compare_data_to_standard

from qqc.qqc.fmriprep import run_fmriprep_on_data

def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    parser = argparse.ArgumentParser(
        description='''Convert dicoms to BIDS

    refresh_qqc.py \\
        --qc_out_dir ${bids_out_dir}/derivatives/quick-qc''',
        formatter_class=RawTextHelpFormatter)

    # image input related options
    parser.add_argument('--qqc_root', '-qr', type=str,
                        help='Quick-QC root directory')
    parser.add_argument('--rerun_qqc', '-rq', action='store_true',
                        help='Rerun QQC on all subjects')

    # extra options
    args = parser.parse_args(argv)
    return args


def re_run_qqc(nifti_session_dir: Path,
               dicom_session_dir: Path,
               qqc_session_path: Path,
               standard_session_dir: Path):
    '''Rerun Quick-QC'''
    # get pydicom information
    df_full = get_dicom_files_walk(dicom_session_dir, True)

    # run within phantom QC
    within_phantom_qc(nifti_session_dir, qqc_session_path)
    df_with_one_series = pd.concat([
        x[1].iloc[0] for x in df_full.groupby('series_num')], axis=1).T
    save_csa(df_with_one_series, qqc_session_path, standard_session_dir)

    standard_session_dir = Path(standard_session_dir)
    df_full_std = jsons_from_bids_to_df(
            standard_session_dir).drop_duplicates()
    df_full_std.sort_values('series_num', inplace=True)

    # check number & order of series
    print('Check number & order of series')
    check_num_order_of_series(df_full, df_full_std, qqc_session_path)

    print('Comparison to standard')
    compare_data_to_standard(nifti_session_dir,
                             standard_session_dir,
                             qqc_session_path)


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    # qqc_summary_for_dpdash(args.qc_out_dir)

    # refresh 'mriqc-combined-mriqc-day1to9999.csv'
    # for mri_root in [Path('/data/predict/data_from_nda/MRI_ROOT'),
                     # Path('/data/predict/data_from_nda_dev/MRI_ROOT')]:
    for mri_root in [Path('/data/predict/data_from_nda/MRI_ROOT')]:
        print(mri_root)
        nifti_root = mri_root / 'rawdata'
        dicom_root = mri_root / 'sourcedata'
        derivatives_root = mri_root / 'derivatives'
        quick_qc_root = derivatives_root / 'quick_qc'
        qqc_subject_paths = quick_qc_root.glob('sub-*')
        qqc_session_paths = quick_qc_root.glob('sub-*/ses-*')

        standard_dir = Path('/data/predict/phantom_human_pilot/rawdata/'
                            'sub-ProNETUCLA/ses-humanpilot')

        dfs = []
        # for qqc_session_path in qqc_session_paths:
        for qqc_subject_path in qqc_subject_paths:
            subject_id = qqc_subject_path.name
            # session_id = qqc_session_path.name

            # nifti_dir = nifti_root / subject_id / session_id
            # dicom_dir = dicom_root / subject_id.split('-')[1] / session_id

            # if re.match(r'^sub-[A-Z]{2}\d{5}$', subject_id) and \
               # re.match(r'^ses-\d{4}\d{2}\d{2}\d{1}$', session_id):
            if re.match(r'^sub-[A-Z]{2}\d{5}$', subject_id):
                try:
                    # df_tmp = qqc_summary_for_dpdash(qqc_session_path)
                    df_tmps = refresh_qqc_summary_for_subject(
                            qqc_subject_path)
                    for df_tmp in df_tmps:
                        dfs.append(df_tmp)
                except:
                    pass
        
        df = pd.concat(dfs)
        df['day'] = range(1, len(df)+1)
        df.to_csv(quick_qc_root / 'combined-AMPSCZ-mriqc-day1to1.csv',
                  index=False)

        df['site'] = df['subject_id'].str[:2]
        for site, table in df.groupby('site'):
            table['day'] = range(1, len(table)+1)
            table.to_csv(quick_qc_root / f'combined-{site}-mriqc-day1to1.csv',
                    index=False)

        pronet_network = ['CA', 'PV', 'CM', 'PA', 'GA',
                          'PI', 'HA', 'SL', 'BI', 'SH',
                          'KC', 'TE', 'MU', 'IR', 'MA',
                          'LA', 'MT', 'SD', 'SI', 'SF',
                          'NL', 'NC', 'NN', 'WU', 'OR', 'YA']

        prescient_network = ['ME', 'AD', 'JE', 'CP', 'BM', 'LS',
                             'GW', 'SG', 'HK', 'CG', 'ST']

        df = df.reset_index()
        for index, row in df.iterrows():
            if row['site'] in pronet_network:
                df.loc[index, 'network'] = 'PRONET'
            elif row['site'] in prescient_network:
                df.loc[index, 'network'] = 'PRESCIENT'
            else:
                df.loc[index, 'network'] = '-'

        for network, table in df.groupby('network'):
            table['day'] = range(1, len(table)+1)
            table.drop('index', axis=1).to_csv(
                    quick_qc_root / f'combined-{network}-mriqc-day1to1.csv',
                    index=False)



    # rerun missing eddyqc / fmriprep / eddydf
    # no_fmriprep_df = df[
            # df.framewise_displacement_fMRI_AP_1.isnull()]

    # fmriprep_outdir_root = derivatives_root / 'fmriprep'
    # fs_outdir_root = derivatives_root / 'freesurfer'
    # for _, row in no_fmriprep_df.iterrows():
        # run_fmriprep_on_data(
            # nifti_root,
            # 'sub-' + row['subject_id'],
            # 'ses-' + row['session_id'],
            # fmriprep_outdir_root,
            # fs_outdir_root)

    # no_eddy_df = df[df.Absolute_dwi_motion.isnull()]
    # for _, row in no_eddy_df.iterrows():
        # dwipreproc_outdir_root = derivatives_root / 'dwipreproc'
        # run_quick_dwi_preproc_on_data(
            # nifti_root,
            # 'sub-' + row['subject_id'],
            # 'ses-' + row['session_id'],
            # dwipreproc_outdir_root)


    # no_mriqc_df = df[df.cnr_T2w.isnull()]
    # for _, row in no_mriqc_df.iterrows():
        # mriqc_outdir_root = derivatives_root / 'mriqc'
        # run_mriqc_on_data(
            # nifti_root,
            # 'sub-' + row['subject_id'],
            # 'ses-' + row['session_id'],
            # mriqc_outdir_root)


