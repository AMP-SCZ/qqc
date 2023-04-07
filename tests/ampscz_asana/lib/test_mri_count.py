from ampscz_asana.lib.server_scanner import get_all_mri_zip, \
        get_most_recent_file, get_all_subjects_with_consent
from ampscz_asana.lib.mri_count import get_mri_zip_df, \
        get_mri_zip_df_pivot_for_subject, create_dpdash_mri_zip_df_pivot, \
        add_qc_measures, get_mriqc_value_df_pivot_for_subject, \
        create_dpdash_eeg_zip_df_pivot, create_dpdash_zip_df_pivot
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
    mriqc_value_df = add_qc_measures(mri_zip_df, mriqc_value_loc)
    mriqc_value_df_pivot = get_mriqc_value_df_pivot_for_subject(
            mriqc_value_df, outpath)
