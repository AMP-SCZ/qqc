from ampscz_asana.lib.qc import date_of_zip, get_run_sheet_df, get_mri_path, \
    date_of_qqc
import pandas as pd
from pathlib import Path
from dataflow_checker.ampscz_mri_file import get_matching_timepoint
import pytest


class FakePhoenixSubject:
    def __init__(self, outdir='PHOENIX', network='Pronet',
                 subject='AB12345', date='2023_01_01'):
        outpath = Path(outdir)
        self.root_dir = outpath
        self.fake_subject = subject
        self.date = date
        self.protected_raw_mri = outpath / 'PROTECTED' / \
                (network + self.fake_subject[:2]) / 'raw' / \
                self.fake_subject / 'mri'
        self.zip_path = self.protected_raw_mri / \
                f'{self.fake_subject}_MR_{self.date}_1.zip'

        self.zip_path.parent.mkdir(exist_ok=True, parents=True)
        self.zip_path.touch()


# @pytest.fixture
# def get_fake_phoenix_data():
    # return [Fruit("apple"), Fruit("banana")]


def test_date_of_zip():
    phoenix_test_root = 'PHOENIX'
    fakePhoenixSubject = FakePhoenixSubject(
            outdir=phoenix_test_root, network='Pronet', subject='TE00307',
            date='2023_01_01')

    assert(date_of_zip('TE00307',
                       '2022_10_20',
                       phoenix_test_root)) == '2022-11-12'
    # assert(date_of_zip('LA07315', '2022_12_16', phoenix_root)) == '2022-12-17'


    # phoenix_root = '/data/predict1/data_from_nda/Prescient/PHOENIX'
    # assert(date_of_zip('ME04934', '2022_12_02', phoenix_root)) == '2023-03-13'
    # assert(date_of_zip('CP01128', '2023_02_23', phoenix_root)) == '2023-03-02'


def test_date_of_qqc():
    subject = 'ME79913'
    entry_date = '2022_12_16'
    date_of_qqc_out = date_of_qqc(subject, entry_date)
    print(date_of_qqc_out)


def hatest_get_run_sheet():
    phoenix_root = Path('/data/predict1/data_from_nda/Prescient/PHOENIX')
    run_sheet_csv_tmp = Path('test.csv')

    # if run_sheet_csv_tmp.is_file():
    # run_sheet_df = pd.read_csv(run_sheet_csv_tmp)
    run_sheet_df = get_run_sheet_df(phoenix_root)
    run_sheet_df.to_csv(run_sheet_csv_tmp)
    # else:
        # run_sheet_df = get_run_sheet_df(phoenix_root)
        # run_sheet_df.to_csv(run_sheet_csv_tmp)

    cols_to_print = ['file_path',
                     'subject',
                     'mri_data_path',
                     'mri_data_multises',
                     'other_files',
                     'entry_date',
                     'mri_data_exist',
                     'zip_date',
                     'qqc_date',
                     'timepoint']

    df_tmp = run_sheet_df[cols_to_print]  #.tail()  #.head()
    print(df_tmp)
    df_target = df_tmp.pivot_table(
            index=['subject'],
            values=['entry_date', 'zip_date', 'qqc_date'],
            columns=['timepoint'],
            aggfunc=lambda x: x).reorder_levels([1, 0], axis=1).sort_index(axis=1)
    print(df_target)
