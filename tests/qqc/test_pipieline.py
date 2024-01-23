from pathlib import Path
from qqc.pipeline import dicom_to_bids_QQC, run_qqc


def test():
    pass


def test_run_qqc():
    qc_out_dir = Path(
            '/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/sub-CA00152/ses-202301041')
    nifti_session_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-CA00152/ses-202301041')
    # df_full = '/data/predict1/data_from_nda/MRI_ROOT/derivatives/rawdata/sub-CA00152/ses-202301041'
    from qqc.qqc.json import jsons_from_bids_to_df
    df_full = jsons_from_bids_to_df(nifti_session_dir).drop_duplicates()
    print(df_full)
    return
    standard_dir = Path('/data/predict1/home/kcho/MRI_site_cert/qqc_output/rawdata/sub-GA/ses-202211031')

    run_qqc(qc_out_dir, nifti_session_dir, df_full, standard_dir)



def test_smoothness_run_qqc():
    qc_out_dir = Path('test')
    if not qc_out_dir.is_dir():
        qc_out_dir.mkdir()
    nifti_session_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-WU27051/ses-202312061')
    # df_full = '/data/predict1/data_from_nda/MRI_ROOT/derivatives/rawdata/sub-CA00152/ses-202301041'
    from qqc.qqc.json import jsons_from_bids_to_df
    df_full = jsons_from_bids_to_df(nifti_session_dir).drop_duplicates()
    standard_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-WU04342/ses-202210101')
    run_qqc(qc_out_dir, nifti_session_dir, df_full, standard_dir)


def test_smoothness_run_qqc_error():
    qc_out_dir = Path('test')
    if not qc_out_dir.is_dir():
        qc_out_dir.mkdir()
    nifti_session_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-SF29950/ses-202401041')
    # df_full = '/data/predict1/data_from_nda/MRI_ROOT/derivatives/rawdata/sub-CA00152/ses-202301041'
    from qqc.qqc.json import jsons_from_bids_to_df
    df_full = jsons_from_bids_to_df(nifti_session_dir).drop_duplicates()
    standard_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-SF10428/ses-202301181')
    run_qqc(qc_out_dir, nifti_session_dir, df_full, standard_dir)
