from ampscz_asana.lib.server_scanner import get_all_mri_zip, \
        get_most_recent_file, get_all_subjects_with_consent
from ampscz_asana.lib.mri_count import get_mri_zip_df, \
        get_mri_zip_df_pivot_for_subject, create_dpdash_zip_df_pivot, \
        add_qc_measures, get_mriqc_value_df_pivot_for_subject
import pandas as pd
from pathlib import Path
import logging
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
logging.basicConfig(format=formatter, handlers=[logging.StreamHandler()])
logging.getLogger().setLevel(logging.DEBUG)

pd.set_option('display.max_columns', 50)


def test_get_mri_zip_df():
    data_root = Path('/data/predict1/data_from_nda')
    phoenix_paths = [data_root / 'Pronet/PHOENIX',
                     data_root / 'Prescient/PHOENIX']
    mriflow_csv = data_root / 'MRI_ROOT/flow_check/mri_data_flow.csv'
    dpdash_outpath = data_root / 'MRI_ROOT/eeg_mri_count'

    eeg_zip_df = get_mri_zip_df(phoenix_paths, mriflow_csv)
    eeg_zip_df_pivot = get_mri_zip_df_pivot_for_subject(eeg_zip_df,
                                                        phoenix_paths)
    create_dpdash_zip_df_pivot(eeg_zip_df_pivot,
                               dpdash_outpath)


def test_get_eeg_zip_df():
    data_root = Path('/data/predict1/data_from_nda')
    phoenix_paths = [data_root / 'Pronet/PHOENIX',
                     data_root / 'Prescient/PHOENIX']
    mriflow_csv = data_root / 'MRI_ROOT/flow_check/mri_data_flow.csv'
    dpdash_outpath = data_root / 'MRI_ROOT/eeg_mri_count'

    eeg_zip_df = get_mri_zip_df(phoenix_paths, mriflow_csv, modality='eeg')
    eeg_zip_df_pivot = get_mri_zip_df_pivot_for_subject(eeg_zip_df,
                                                        phoenix_paths,
                                                        modality='eeg')
    create_dpdash_zip_df_pivot(eeg_zip_df_pivot,
                               dpdash_outpath,
                               modality='eeg')


def test_add_qc_measures():
    data_root = Path('/data/predict1/data_from_nda')
    phoenix_paths = [data_root / 'Pronet/PHOENIX',
                     data_root / 'Prescient/PHOENIX']
    mriflow_csv = data_root / 'MRI_ROOT/flow_check/mri_data_flow.csv'
    mriqc_dir = data_root / 'MRI_ROOT/derivatives/google_qc'

    mri_zip_df = get_mri_zip_df(phoenix_paths, mriflow_csv)
    mriqc_value_loc = get_most_recent_file(mriqc_dir)

    # outpath = Path('test')
    outpath = Path('/data/predict1/data_from_nda/MRI_ROOT/eeg_mri_count')
    mriqc_value_df = add_qc_measures(mri_zip_df, mriqc_value_loc, test=True)

    print(mriqc_value_df[mriqc_value_df.subject_id == 'PI16053'])
    return

    mriqc_value_df_pivot = get_mriqc_value_df_pivot_for_subject(
            mriqc_value_df, outpath)

    print(mriqc_value_df.head())


def test_duplicated_sessions():
    # outpath = Path('test')
    outpath = Path('/data/predict1/data_from_nda/MRI_ROOT/eeg_mri_count')
    zip_df_loc = outpath / 'mri_zip_db.csv'

    df = pd.read_csv(zip_df_loc)

    # count logic
    count_df = df.groupby(['subject_id', 'scan_date']).count()
    more_than_one_subj_df = count_df[count_df.zip_path > 1]
    print(more_than_one_subj_df.index.get_level_values(0))
    df_tmp = df[
        (df.subject_id.isin(more_than_one_subj_df.index.get_level_values(0))) &
        (df.scan_date.isin(more_than_one_subj_df.index.get_level_values(1)))
            ]
    df_tmp.to_csv('test.csv')
    print(df_tmp)

    # print(df)


def test_timepoint_missing_sessions():
    data_root = Path('/data/predict1/data_from_nda')
    phoenix_paths = [data_root / 'Pronet/PHOENIX',
                     data_root / 'Prescient/PHOENIX']
    mriflow_csv = data_root / 'MRI_ROOT/flow_check/mri_data_flow.csv'

    eeg_zip_df = get_mri_zip_df(phoenix_paths, mriflow_csv, test=False)
    # print(eeg_zip_df)
    eeg_zip_df.to_csv('test2.csv')
