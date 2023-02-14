from qqc.pipeline import get_information_from_rawdata
from qqc.qqc.dicom import check_order_of_series
from pathlib import Path

print()


def test_get_fake_df_full_input_and_standard():
    mri_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
    rawdata_root = mri_root / 'rawdata'
    example_nifti_dir = rawdata_root / 'sub-YA16301/ses-202302091'
    example_nifti_dir = rawdata_root / 'sub-ME33795/ses-202302031'
    df_full_input = get_information_from_rawdata(example_nifti_dir)

    mri_root = Path('/data/predict1/home/kcho/MRI_site_cert/qqc_output')
    template_path = mri_root / 'rawdata/sub-LS/ses-202211071'
    # /data/predict1/home/kcho/MRI_site_cert/qqc_output/rawdata/sub-LS/ses-202211071

    df_full_std = get_information_from_rawdata(template_path)
    # print(df_full_std)

    order_check_df = check_order_of_series(df_full_input, df_full_std)
    print(order_check_df)
    print(order_check_df.columns)
