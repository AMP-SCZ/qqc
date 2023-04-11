from qqc.qqc.json import jsons_from_bids_to_df
from qqc.dicom_files import get_dicom_files_walk, get_csa_header
from qqc.qqc.dicom import check_num_of_series, \
        check_order_of_series, save_csa, check_image_fov_pos_ori_csa, \
        is_enhanced
import pandas as pd
from pathlib import Path
import socket


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


def test_cehck_num_order_of_series():
    df_full_std = jsons_from_bids_to_df(standard_dir).drop_duplicates()
    df_full_std.sort_values('series_num', inplace=True)

    df_full_input_file = Path('.df_full_input_csv')
    if df_full_input_file.is_file():
        df_full_input = pd.read_csv(df_full_input_file, index_col=0)
    else:
        df_full_input = get_dicom_files_walk(raw_dicom_dir, True)
        df_full_input.to_csv(df_full_input_file)

    num_check_df = check_num_of_series(df_full_input, df_full_std)
    order_check_df = check_order_of_series(df_full_input, df_full_std)

    print()
    print(num_check_df)
    print(order_check_df)


def test_csa_headers():

    # input_dicom_dir = Path(
            # '/data/predict/phantom_human_pilot/sourcedata/'
            # 'ProNET_UCSF_Prisma/ses-phantom'
            # )
    # df_full_input = get_dicom_files_walk(input_dicom_dir, True)
    # save_csa(df_full_input, Path('UCSF_phantom'))

    # input_dicom_dir = Path(
            # '/data/predict/kcho/flow_test/MRI_ROOT/'
            # 'sourcedata/SF11111/ses-202201261')
    # df_full_input = get_dicom_files_walk(input_dicom_dir, True)
    # save_csa(df_full_input, Path('SF11111'))


    # input_dicom_dir = Path(
            # '/data/predict/phantom_data/site_data/'
            # 'ProNET_UCSF_Prisma/human_pilot/data/dicom')
    # df_full_input = get_dicom_files_walk(input_dicom_dir, True)
    # save_csa(df_full_input, Path('SF00003'))


    import pydicom
    dicom_root_path = Path('/data/predict/kcho/flow_test/MRI_ROOT/sourcedata/SF11111/ses-202201261')

    for series_desc_path in dicom_root_path.glob('*'):
        dicom_loc = list(series_desc_path.glob('*'))[0]
        #'/data/predict/kcho/flow_test/MRI_ROOT/sourcedata/SF11111/ses-202201261/16_T2w_SPC/IM-0016-0001.dcm'
        dicom_obj = pydicom.read_file(str(dicom_loc))
        try:
            df = get_csa_header(dicom_obj)
            print(df)
            print(series_desc_path)
            # break
        except:
            print('*'*80)
            print(series_desc_path)
            print('no header')
            print('*'*80)



def test_check_image_fov_pos_ori_csa():
    csa_df_loc = Path('/data/predict/data_from_nda/MRI_ROOT/derivatives/quick_qc/sub-YA05293/ses-202209261/99_csa_headers.csv')
    standard_dir = Path('/data/predict/data_from_nda/MRI_ROOT/rawdata/sub-PI01155/ses-202208311')
    check_image_fov_pos_ori_csa(csa_df_loc, standard_dir)


def test_is_enhanced():
    source_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/sourcedata')
    me_paths = source_dir.glob('ME*')

    for me_path in me_paths:
        print(me_path, is_enhanced(me_path))

