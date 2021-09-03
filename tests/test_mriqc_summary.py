from phantom_check.utils.files import \
        load_anat_json_from_mriqc, \
        load_and_filter_anat_qc_from_open_data, \
        load_anat_jsons_from_mriqc, \
        add_open_data_qc_measures
from phantom_check.utils.visualize import \
        plot_anat_jsons_from_mriqc, plot_anat_jsons_from_mriqc_with_opendata

import sys
from pathlib import Path
import phantom_check
scripts_dir = Path(phantom_check.__file__).parent.parent / 'scripts'
sys.path.append(str(scripts_dir))

from summarize_mriqc_measures import plot_with_open_data
from summarize_mriqc_measures import parse_args
import pytest


@pytest.fixture
def get_files():
    # alter here if you have to
    open_data_root = Path(phantom_check.__file__).parent.parent / 'data'
    test_data_root = Path('/Users/kc244/phantom_mriqc_test/out')

    t1_csv_loc = open_data_root / 'T1w_demo.csv'
    mri_qc_jsons = [
            test_data_root / 'sub-singapore01/anat/sub-singapore01_T1w.json',
            test_data_root / 'sub-ucla02/anat/sub-ucla02_T1w.json']

    return t1_csv_loc, mri_qc_jsons


def test_load_anat_json_from_mriqc(get_files):
    mri_qc_jsons = get_files[1]
    print()
    load_anat_json_from_mriqc(mri_qc_jsons[0])


def test_load_anat_jsons_from_mriqc(get_files):
    mri_qc_jsons = get_files[1]
    load_anat_jsons_from_mriqc(mri_qc_jsons)
    pass


def test_plot_anat_jsons_from_mriqc(get_files):
    mri_qc_jsons = get_files[1]
    df = load_anat_jsons_from_mriqc(mri_qc_jsons)
    print(df)
    plot_anat_jsons_from_mriqc(df)


def test_load_and_filter_anat_qc_from_open_data(get_files):
    csv_loc = get_files[0]
    df = load_and_filter_anat_qc_from_open_data(csv_loc)
    print(df)


def test_columns_from_open_data_and_mriqc(get_files):
    csv_loc = get_files[0]
    mri_qc_jsons = get_files[1]
    df_open = load_and_filter_anat_qc_from_open_data(csv_loc)
    df_mri_qc = load_anat_jsons_from_mriqc(mri_qc_jsons)
    df_open = df_open[[x for x in df_open.columns if not x.startswith('bids_meta')]]

    diff = [x for x in df_mri_qc.index if x not in df_open.columns]
    assert len(diff) == 0



def test_add_open_data(get_files):
    csv_loc = get_files[0]
    mri_qc_jsons = get_files[1]

    df_open = load_and_filter_anat_qc_from_open_data(csv_loc)
    df_mri_qc = load_anat_jsons_from_mriqc(mri_qc_jsons)
    df = add_open_data_qc_measures(df_mri_qc, df_open)


def test_add_open_data_plot(get_files):
    csv_loc = get_files[0]
    mri_qc_jsons = get_files[1]
    df_open = load_and_filter_anat_qc_from_open_data(csv_loc)
    df_mri_qc = load_anat_jsons_from_mriqc(mri_qc_jsons)
    df = add_open_data_qc_measures(df_mri_qc, df_open)
    g = plot_anat_jsons_from_mriqc_with_opendata(df, 'tmp.png')


@pytest.fixture
def test_argparse(get_files):
    csv_loc = get_files[0]
    mri_qc_jsons = get_files[1]

    parser = parse_args(
            ['--mri_qc_jsons'] + [str(x) for x in mri_qc_jsons] +
            ['--opendata_csv', str(csv_loc), '--out_image', 'tmp.png'])
    
    return parser


def test_executable(test_argparse):
    plot_with_open_data(test_argparse)

