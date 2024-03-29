from qqc.utils.files import get_all_files_walk
from qqc.qqc.json import jsons_from_bids_to_df, within_phantom_qc, \
        get_all_json_information_quick, json_check, \
        find_matching_files_between_BIDS_sessions, \
        compare_jsons_to_std, json_check_new, \
        compare_data_to_standard_all_bvals
from qqc.dicom_files import get_dicom_files_walk
from qqc.qqc.dicom import check_num_of_series, check_order_of_series
import pandas as pd
from pathlib import Path
import socket
import json


import logging
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
logging.basicConfig(format=formatter, handlers=[logging.StreamHandler()])
logging.getLogger().setLevel(logging.INFO)

if socket.gethostname() == 'mbp16':
    raw_dicom_dir = Path(__file__).parent.parent.parent / 'data' / \
            'dicom_raw_source'

    standard_dir = Path(__file__).parent.parent.parent / 'data' / \
            'dicom_raw_source'
else:
    raw_dicom_dir = Path('/data/predict/phantom_data'
                         '/kcho/tmp/PHANTOM_20211022')
    standard_dir = Path('/data/predict/phantom_human_pilot/rawdata'
                        '/sub-ProNETUCLA/ses-humanpilot')


def test_json_check_for_a_session():
    json_files = get_all_files_walk(standard_dir, 'json')
    within_phantom_qc(Path(standard_dir), Path('test'))


def test_compare_data_to_standard_all_bvals():

    data_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    input_dir = data_root / 'rawdata/sub-CP01128/ses-202302231/dwi'

    std_root = Path('/data/predict1/home/kcho/MRI_site_cert/CP_data') / \
            'lochness_transfer_2023_02'
    standard_dir = std_root / 'CP01128_MR_2023_02_23_1/CP01128' / \
            'heudiconv_out_new_new_MathiasHelp/sub-CP01128/ses-clean_up/dwi'
    qc_output_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/sub-CP01128/ses-202302231')
    compare_data_to_standard_all_bvals(input_dir,
            standard_dir, qc_output_dir, debug=True)
# def json_check_new(json_files: list, diff_only=True) -> pd.DataFrame:
    # '''Compare list of json files and return dataframe

    # Key Arguments:
        # json_files: list of json files, list of Path.
        # diff_only: return different values only
    # '''
    # to_drop_list = [
        # 'AcquisitionTime', 'ImageOrientationPatientDicom',
        # 'ImageOrientationPatientDICOM',
        # 'SliceTiming',
        # 'global', 'TxRefAmp',
        # 'dcmmeta_affine', 'WipMemBlock',
        # 'SAR', 'time']

    # dicts = []
    # cols = []
    # series_desc_list = []
    # for i in json_files:
        # cols.append(i.name)
        # with open(i, 'r') as f:
            # single_dict = json.load(f)
            # dicts.append(single_dict)

    # df_tmp = pd.DataFrame(dicts).T
    # for i in to_drop_list:
        # if i in df_tmp.index:
            # df_tmp.drop(i, inplace=True)

    # df_tmp.columns = cols

    # if diff_only:
        # df_tmp = df_tmp[(df_tmp[cols[0]] != df_tmp[cols[1]])]

    # return df_tmp


def test_find_matching_files_between_BIDS_sessions():

    input_dir = '/data/predict/kcho/flow_test/MRI_ROOT/rawdata/' \
            'sub-YA00009/ses-202107231'

    # input_dir = '/data/predict/kcho/flow_test/MRI_ROOT/sourcedata/PA00022/ses-202112141'
    qc_out_dir = Path('.')
    json_df_input = get_all_json_information_quick(input_dir)
    json_df_std = get_all_json_information_quick(standard_dir)

    json_df_all = pd.merge(
        json_df_input, json_df_std,
        how='outer',
        on=['series_desc', 'image_type', 'run_num', 'scout_num'],
        suffixes=['_input', '_std'])

    df_diff = pd.DataFrame()
    for _, row in json_df_all.iterrows():
        df_row = json_check_new([row.json_path_input, row.json_path_std])
        df_row.columns = ['input', 'std']
        df_row['series_desc'] = row['series_desc']
        df_row['series_num'] = row['series_num_input']
        df_row['input_json'] = row['json_path_input'].name
        df_row['standard_json'] = row['json_path_std'].name
        df_row = df_row.reset_index().set_index(
                ['series_desc', 'series_num', 'input_json',
                 'standard_json', 'index'])
        df_diff = pd.concat([df_diff, df_row], axis=0)

    df_diff.to_excel(qc_out_dir / 'json_comparison_log.xlsx')


def test_find_matching_files_between_BIDS_sessions_two():
    input_dir = '/data/predict/kcho/flow_test/MRI_ROOT/rawdata/sub-PA00022/ses-202112141'
    json_df_all = find_matching_files_between_BIDS_sessions(input_dir, standard_dir)
    json_df_all.to_csv('test.csv')
    print(Path('test.csv').absolute())


def test_find_matching_between_BIDS_and_nonBIDS():
    input_dir = Path('/data/predict1/home/kcho/MRI_site_cert/AD_data/dcm2niix_output')
    standard_dir = Path('/data/predict1/home/kcho/MRI_site_cert/qqc_output/rawdata/sub-AD00001/ses-202109061')
    json_df_all = find_matching_files_between_BIDS_sessions(input_dir, standard_dir)
    json_df_all.to_csv('test.csv')

def test_find_matching_files_between_BIDS_sessions_after_xa30():
    input_dir = '/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-WU09114/ses-202301101'
    standard_dir = '/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-WU04342/ses-202210101'
    json_df_all = find_matching_files_between_BIDS_sessions(input_dir, standard_dir)
    json_df_all.to_csv('test.csv')
    print(Path('test.csv').absolute())

def test_find_matching_files_between_BIDS_sessions_missing_input():
    print()
    pd.set_option('max_columns', 50)
    import numpy as np
    input_dir = '/data/predict/kcho/flow_test/MRI_ROOT/rawdata/sub-PA00022/ses-202112141'
    json_df_input = get_all_json_information_quick(input_dir)
    json_df_input = json_df_input.iloc[:-3]
    json_df_std = get_all_json_information_quick(standard_dir)

    json_df_all = pd.merge(
        json_df_input, json_df_std,
        how='left',
        on=['series_desc', 'image_type', 'run_num',
            'num_num', 'scout_num', 'distortion_map_before'],
        suffixes=['_input', '_std'])

    for index, row in json_df_all.iterrows():
        # When there is extra distortion map, the number in front of run_num
        # does not match to that of standard distortion maps. So, distortion
        # maps do not get matched properly. Iterate non-matched distortion maps
        if pd.isnull(row.json_path_std) and \
                'distort' in row.series_desc.lower():
            # get dataframe of standard distortion maps in the same position
            # eg.) distortion maps before T1w_MPR or rfMRI_REST
            df_tmp = json_df_std[
                (json_df_std.series_desc == row.series_desc) &
                (json_df_std.distortion_map_before == \
                        row.distortion_map_before)]

            # find the standard distortion map with most close series number
            diff_in_series_num = 100
            for df_tmp_index, r2 in df_tmp.iterrows():
                diff = row.series_num_input - r2.series_num
                if np.absolute(diff) < diff_in_series_num:
                    json_df_all.loc[index, 'json_path_std'] = r2.json_path
                    json_df_all.loc[index, 'json_suffix_std'] = r2.json_suffix
                    json_df_all.loc[index, 'series_num_std'] = r2.series_num
                    diff_in_series_num = diff

    
    # standard series not included in the input series
    for num, (index, row) in enumerate(json_df_std[
            ~json_df_std.json_suffix.isin(json_df_all.json_suffix_std)
            ].iterrows(), 1):
        new_index = json_df_all.index[-1] + num
        for var in ['image_type', 'series_num', 'run_num', 'num_num',
                'scout_num', 'distortion_map_before']:
            json_df_all.loc[new_index, var] = row[var]

        for var in ['json_path', 'json_suffix', 'series_num']:
            json_df_all.loc[new_index, f'{var}_std'] = row[var]


    json_df_all.sort_values(
            ['series_num_input', 'run_num', 'scout_num'],
            inplace=True)

    return json_df_all


def test_compare_data_to_standard_all_json_new():
    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    rawdata_dir = root_dir / 'rawdata/sub-SF11111/ses-202201261'
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-SF11111/ses-202201261'

    # rawdata_dir = root_dir / 'rawdata/sub-NL00000/ses-202112071'
    # qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-NL00000/ses-202112071'

    # rawdata_dir = root_dir / 'rawdata/sub-BM00016/ses-202111171'
    # qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-BM00016/ses-202111171'
    
    root_dir = Path('/data/predict/phantom_data/site_data/'
                    'ProNET_Calgary_GE/human_pilot/dicom/second_transfer/MRI_ROOT2')
    rawdata_dir = root_dir / 'rawdata/sub-CG/ses-1'
    qqc_out_dir = root_dir / 'derivatives2/quick_qc/sub-CG/ses-1'

    standard_dir = Path('/data/predict/phantom_human_pilot/rawdata/sub-PrescientAdelaideSkyra')
    within_phantom_qc(rawdata_dir, qqc_out_dir)
    compare_jsons_to_std(rawdata_dir, standard_dir, qqc_out_dir)

def test_sub_CG():
    df_diff = pd.DataFrame()

    json_files = [
        '/data/predict/phantom_data/site_data/ProNET_Calgary_GE'
            '/human_pilot/dicom/test/rawdata/sub-CG/ses-1/dwi'
            '/sub-CG_ses-1_acq-b0_dir-AP_run-1.json',
        '/data/predict/phantom_human_pilot/rawdata/sub-PrescientAdelaideSkyra'
        '/ses-humanpilot/dwi/sub-PrescientAdelaideSkyra_ses-humanpilot'
        '_acq-b0_dir-AP_run-1_dwi.json'
        ]

    df_row = json_check_new([Path(x) for x in json_files])
    df_row.columns = ['input', 'std']
    df_row['series_desc'] = 'b0_AP'
    df_row['series_num'] = 6
    df_row['input_json'] = Path(json_files[0]).name
    df_row['standard_json'] = Path(json_files[1]).name

    df_row = df_row.reset_index().set_index(
        ['series_desc', 'series_num', 'input_json',
         'standard_json', 'index'])

    df_diff = pd.concat([df_diff, df_row], axis=0)

    json_files = [
        '/data/predict/phantom_data/site_data/ProNET_Calgary_GE/human_pilot/'
        'dicom/test/rawdata/sub-CG/ses-1/dwi/sub-CG_ses-1_acq-126_dir_PA_run-1_dwi.json',
        '/data/predict/phantom_human_pilot/rawdata/sub-PrescientAdelaideSkyra'
        '/ses-humanpilot/dwi/sub-PrescientAdelaideSkyra_ses-humanpilot_acq-126_dir-PA_run-1_dwi.json'
        ]

    df_row = json_check_new([Path(x) for x in json_files])
    df_row.columns = ['input', 'std']
    df_row['series_desc'] = 'dMRI_dir126_PA'
    df_row['series_num'] = 8
    df_row['input_json'] = Path(json_files[0]).name
    df_row['standard_json'] = Path(json_files[1]).name

    df_row = df_row.reset_index().set_index(
        ['series_desc', 'series_num', 'input_json',
         'standard_json', 'index'])

    df_diff = pd.concat([df_diff, df_row], axis=0)
    df_diff.to_csv('CG_ses_1_test.csv')

    print(df_diff)
 

def test_compare_philips_and_GE_KCL_GA():
    root_dir = Path('/data/predict/kcho/philips/new_unzip/Philips_Copenhagen_20220908_test/BIDS')
    rawdata_dir = root_dir / 'rawdata/sub-cp/ses-20220908'
    qqc_out_dir = root_dir

    # within_phantom_qc(rawdata_dir, qqc_out_dir)
    within_phantom_qc(
            Path('/data/predict/phantom_data/kcho/GE_experiment/GA/dcm2niix_output'),
            Path('/data/predict/phantom_data/kcho/GE_experiment/GA/dcm2niix_output'))

    within_phantom_qc(
            Path('/data/predict/phantom_data/kcho/GE_experiment/KCL/dcm2niix_output'),
            Path('/data/predict/phantom_data/kcho/GE_experiment/KCL/dcm2niix_output'))
    


    standard_dir = Path('/data/predict/data_from_nda/MRI_ROOT/rawdata/sub-YA01508/ses-202208261')
    # compare_jsons_to_std(rawdata_dir, standard_dir, qqc_out_dir)

def test_compare_philips_within_phantom():
    rawdata_dir = Path(
            '/data/predict/kcho/philips/new_unzip/'
            'Philips_Copenhagen_20220908_test/BIDS/'
            'rawdata/sub-cp/ses-20220908')
    within_phantom_qc(
            rawdata_dir,
            Path('/data/predict/kcho/philips/new_unzip/Philips_Copenhagen_20220908_test/BIDS'))
    qqc_out_dir = Path('/data/predict/kcho/philips/new_unzip/Philips_Copenhagen_20220908_test/BIDS')
    standard_dir = Path('/data/predict/data_from_nda_dev/MRI_ROOT/rawdata/sub-AD00001/ses-202109061')
    compare_jsons_to_std(rawdata_dir, standard_dir, qqc_out_dir)


def test_image_orientation_roundup():
    input_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-ME97666/ses-202212202')
    qc_out_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/sub-ME97666/ses-202212202')
    within_phantom_qc(
            input_dir,
            qc_out_dir)


def test_compare_jsons_to_std():
    rawdata_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-ME54434/ses-202301062')
    standard_dir = Path('/data/predict1/home/kcho/MRI_site_cert/qqc_output/rawdata/sub-LS/ses-202211071')
    qqc_out_dir = 'qc_test'
    compare_jsons_to_std(rawdata_dir, standard_dir, qqc_out_dir)


def test_within_phantom_qc_cp():
    data_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    input_dir = data_root / 'rawdata/sub-CP01128/ses-202302231/dwi'

    std_root = Path('/data/predict1/home/kcho/MRI_site_cert/CP_data') / \
            'lochness_transfer_2023_02'
    standard_dir = std_root / 'CP01128_MR_2023_02_23_1/CP01128' / \
            'heudiconv_out_new_new_MathiasHelp/sub-CP01128/ses-clean_up/dwi'
    qc_output_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/sub-CP01128/ses-202302231')

    within_phantom_qc(input_dir.parent, qc_output_dir, debug=True)
