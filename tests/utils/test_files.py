from phantom_check.utils.files import load_anat_json_from_mriqc
from phantom_check.utils.files import load_anat_jsons_from_mriqc
from phantom_check.utils.files import load_and_filter_anat_qc_from_open_data
from phantom_check.utils.files import add_open_data_qc_measures
from phantom_check.utils.visualize import plot_anat_jsons_from_mriqc
from phantom_check.utils.visualize import plot_anat_jsons_from_mriqc_with_opendata

import pandas as pd
from pathlib import Path
pd.set_option('max_rows', 5000)


def test_load_anat_json_from_mriqc():
    print()
    load_anat_json_from_mriqc('/Users/kc244/phantom_mriqc_test/out/sub-singapore01/anat/sub-singapore01_T1w.json')
    pass

def test_load_anat_jsons_from_mriqc():
    print()
    load_anat_jsons_from_mriqc(
            ['/Users/kc244/phantom_mriqc_test/out/sub-singapore01/anat/sub-singapore01_T1w.json',
             '/Users/kc244/phantom_mriqc_test/out/sub-ucla02/anat/sub-ucla02_T1w.json'])

    pass


def test_plot_anat_jsons_from_mriqc():
    print()
    df = load_anat_jsons_from_mriqc(
            ['/Users/kc244/phantom_mriqc_test/out/sub-singapore01/anat/sub-singapore01_T1w.json',
             '/Users/kc244/phantom_mriqc_test/out/sub-ucla02/anat/sub-ucla02_T1w.json'])
    print(df)
    plot_anat_jsons_from_mriqc(df)


def test_load_and_filter_anat_qc_from_open_data():
    csv_loc = '/Users/kc244/phantom_check/data/T1w_demo.csv'
    df = load_and_filter_anat_qc_from_open_data(csv_loc)
    print(df)


def test_columns_from_open_data_and_mriqc():
    csv_loc = '/Users/kc244/phantom_check/data/T1w_demo.csv'
    df_open = load_and_filter_anat_qc_from_open_data(csv_loc)
    df_mri_qc = load_anat_jsons_from_mriqc(
            ['/Users/kc244/phantom_mriqc_test/out/sub-singapore01/anat/sub-singapore01_T1w.json',
             '/Users/kc244/phantom_mriqc_test/out/sub-ucla02/anat/sub-ucla02_T1w.json'])

    df_open = df_open[[x for x in df_open.columns if not x.startswith('bids_meta')]]

    diff = [x for x in df_mri_qc.index if x not in df_open.columns]
    import phantom_check
    print(Path(phantom_check.__file__).parent.parent)
    assert len(diff) == 0



def test_add_open_data():
    csv_loc = '/Users/kc244/phantom_check/data/T1w_demo.csv'
    df_open = load_and_filter_anat_qc_from_open_data(csv_loc)
    df_mri_qc = load_anat_jsons_from_mriqc(
            ['/Users/kc244/phantom_mriqc_test/out/sub-singapore01/anat/sub-singapore01_T1w.json',
             '/Users/kc244/phantom_mriqc_test/out/sub-ucla02/anat/sub-ucla02_T1w.json'])
    df = add_open_data_qc_measures(df_mri_qc, df_open)
    print()
    print(df)


def test_add_open_data_plot():
    csv_loc = '/Users/kc244/phantom_check/data/T1w_demo.csv'
    df_open = load_and_filter_anat_qc_from_open_data(csv_loc)
    df_mri_qc = load_anat_jsons_from_mriqc(
            ['/Users/kc244/phantom_mriqc_test/out/sub-singapore01/anat/sub-singapore01_T1w.json',
             '/Users/kc244/phantom_mriqc_test/out/sub-ucla02/anat/sub-ucla02_T1w.json'])
    df = add_open_data_qc_measures(df_mri_qc, df_open)
    g = plot_anat_jsons_from_mriqc_with_opendata(df)



