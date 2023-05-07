from ampscz_asana.lib.qc import date_of_zip, extract_variable_information, extract_missing_data_information, compare_dates, format_days
from ampscz_asana.lib.qc import get_run_sheet_df, extract_missing_data_info_new
from ampscz_asana.lib.qc import is_qqc_executed, dataflow_dpdash, \
        extract_mri_comments
from ampscz_asana.lib.qc import date_of_zip, extract_variable_information, \
        extract_missing_data_information, compare_dates, format_days, \
        check_mri_data

import pandas as pd
from pathlib import Path


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

  assert(date_of_zip('ME04934', '2022_12_02', dir)) == '2023-03-13'
  assert(date_of_zip('CP01128', '2023_02_23', dir)) == '2023-03-02'


def test_extract_missing_data_information():  #will also test the extract_variable_information function since this one uses it 
  dir = '/data/predict1/data_from_nda/Prescient/PHOENIX'
  try:
    assert (extract_missing_data_information('ME97666', str(dir))[0] == 
            "'Timepoint: baseline_arm_1 | Date: 2022-10-14 | clinical measures', 'Timepoint: month_3_arm_1 | Date: | digital biomarkers'")
  except AssertionError:
    print("Assertion failed!")                            
    
  try:
    assert (extract_missing_data_information('ME97666', str(dir))[1] == 
            "'Timepoint: baseline_arm_1 | Date: 2022-10-14 | Other reason', 'Timepoint: month_3_arm_1 | Date: | Other reason'")
  except AssertionError:
    print("Assertion failed!")
  

def test_compare_dates():
    data = {
        'entry_date': ['2022_10_14', '2022_10_15', '2022-11-15'],
        'domain_type_missing': ['"Timepoint: baseline_arm_1 | Date: 2022-10-14 | clinical measures"',
                                '"Timepoint: month_3_arm_1 | Date: | digital biomarkers"',
                                '"Timepoint: month_6_arm_1 | Date: 2022-11-15 | clinical measures"'],
        'reason_for_missing_data': ['','',''],
        'domain_missing' : ['','',''],
        'comments': ['','',''],
        'missing_data_form_complete': ['','','']
    }
    df = pd.DataFrame(data)

    output_df = compare_dates(df)

    try:
        assert set(output_df.columns) == set(data.keys()), "incorrect columns"
        assert output_df.shape[0] == len(data['entry_date']), "incorrect number of rows"
        assert output_df['domain_type_missing'].tolist() == ['Timepoint: baseline_arm_1 | Date: 2022-10-14 | clinical measures', '', 'Timepoint: month_6_arm_1 | Date: 2022-11-15 | clinical measures'], "incorrect values in 'domain_type_missing' column"
        assert output_df['reason_for_missing_data'].tolist() == ['', '', ''], "incorrect values in 'reason_for_missing_data' column"
        assert output_df['domain_missing'].tolist() == ['', '', ''], "incorrect values in 'domain_missing' column"
        assert output_df['comments'].tolist() == ['', '', ''], "incorrect values in 'comments' column"
        assert output_df['missing_data_form_complete'].tolist() == ['', '', ''], "incorrect values in 'missing_data_form_complete' column"
    except AssertionError:
         raise AssertionError(f"Assertion error: {AssertionError}")
    
    print("All tests passed")

    
def test_format_days():
    try:
        assert format_days(5.0) == '5 days'
        assert format_days(1.0) == '1 day'
    except AssertionError:
        raise AssertionError(f"Assertion error: {AssertionError}")


def test_get_run_sheet_df():
    phoenix_root = Path('/data/predict1/data_from_nda/Pronet/PHOENIX')
    df = get_run_sheet_df(phoenix_root)
    df.to_csv('pronet_test.csv')
    print(df)


def test_extract_missing_data_info_new():
    phoenix_root = Path('/data/predict1/data_from_nda/Pronet/PHOENIX')
    subject = 'YA08362'
    scan_date = ''

    print(extract_missing_data_info_new(subject, phoenix_root, scan_date, '1'))

    phoenix_root = Path('/data/predict1/data_from_nda/Prescient/PHOENIX')
    subject = 'BM60731'
    scan_date = ''

    print(extract_missing_data_info_new(subject, phoenix_root, scan_date, '2'))

def test_is_qqc_executed():
    subject = 'YA08362'
    scan_date = ''
    assert is_qqc_executed(subject, scan_date) == False


def test_dataflow_dpdash():
    phoenix_root = Path('/data/predict1/data_from_nda/Pronet/PHOENIX')
    if Path('test_full_df_pronet.csv').is_file():
        df1 = pd.read_csv('test_full_df_pronet.csv')
    else:
        df1 = get_run_sheet_df(phoenix_root)
        df1.to_csv('test_full_df_pronet.csv')

    phoenix_root = Path('/data/predict1/data_from_nda/Prescient/PHOENIX')
    if Path('test_full_df_prescient.csv').is_file():
        df2 = pd.read_csv('test_full_df_prescient.csv')
    else:
        df2 = get_run_sheet_df(phoenix_root)
        df2.to_csv('test_full_df_prescient.csv')

    df = pd.concat([df1, df2])
    dataflow_dpdash(df)


def test_mricomment():
    run_sheet_path = Path('/data/predict1/data_from_nda/Pronet/PHOENIX/PROTECTED/PronetYA/raw/YA08362/mri/YA08362.Pronet.Run_sheet_mri_1.csv')
    extract_mri_comments(run_sheet_path)

    run_sheet_path = Path('/data/predict1/data_from_nda/Prescient/PHOENIX/PROTECTED/PrescientME/raw/ME98165/mri/ME98165.Prescient.Run_sheet_mri_1.csv')
    extract_mri_comments(run_sheet_path)


def test_dpdash_dataflow_view_update():
    phoenix_root = Path('/data/predict1/data_from_nda/Pronet/PHOENIX')
    if Path('test_full_df_pronet.csv').is_file():
        df1 = pd.read_csv('test_full_df_pronet.csv')
    else:
        df1 = get_run_sheet_df(phoenix_root)
        df1.to_csv('test_full_df_pronet.csv')

    all_df = dataflow_dpdash(df1, 'haha', test=True)
    print(all_df.head())


def test_merge_zip_db_and_runsheet_db():
    zip_df = pd.read_csv('/data/predict1/data_from_nda/MRI_ROOT/eeg_mri_count/mri_zip_db.csv',
            index_col=0)
    zip_df.session_num = zip_df.session_num.astype(int)

    def zip_df_rename(col:str) -> str:
        if col == 'subject_id':
            return 'subject'

        if col == 'scan_date_str':
            return 'entry_date'

        return col

    zip_df.columns = [zip_df_rename(x) for x in zip_df.columns]
    runsheet_df = pd.read_csv('/data/predict1/data_from_nda/MRI_ROOT/flow_check/mri_data_flow.csv',
            index_col=0)
    runsheet_df.session_num = runsheet_df.session_num.astype(int)

    all_df = pd.merge(zip_df,
            runsheet_df,
            on=['subject', 'entry_date', 'network', 'session_num'],
            how='outer')

    all_df.to_csv('test_mri_all_db.csv')


def test_check_mri_data():
    test_subject = 'ME84344'
    phoenix_root = Path('/data/predict1/data_from_nda/Prescient/PHOENIX')
    data_root = phoenix_root / 'PROTECTED/PrescientME/raw'
    subject_root = data_root / test_subject
    mri_dir = subject_root / 'mri'
    run_sheet_path = mri_dir / f'{test_subject}.Prescient.Run_sheet_mri_1.csv'

    entry_date = '2023_03_03'

    assert check_mri_data(run_sheet_path, entry_date)

    entry_date = '2023_3_3'
    assert check_mri_data(run_sheet_path, entry_date)

    entry_date = '2023_03_3'
    assert check_mri_data(run_sheet_path, entry_date)

    entry_date = '2023_3_03'
    assert check_mri_data(run_sheet_path, entry_date)
