from qqc.run_sheet import get_matching_run_sheet_path


def test_import():
    pass


def test_prescient_data():
    # data_loc = '/data/predict1/data_from_nda/Prescient/PHOENIX/PROTECTED/PrescientME/raw/ME04934/mri/ME04934_MR_2022_12_2_1.ZIP'
    data_loc = '/data/predict1/data_from_nda/Prescient/PHOENIX/PROTECTED/PrescientME/raw/ME54434/mri/ME54434_MR_2023_01_06_2.zip'
    run_sheet = get_matching_run_sheet_path(data_loc, '2022_12_2_1')
    print(run_sheet)


def test_pronet_data():
    data_loc = '/data/predict1/data_from_nda/Pronet/PHOENIX/PROTECTED/PronetYA/raw/YA01508/mri/YA01508_MR_2022_06_23_1.zip'
    run_sheet = get_matching_run_sheet_path(data_loc, '2022_06_23_1')
    print(run_sheet)



def test_me_error_data():
    data_loc = '/data/predict1/data_from_nda/Prescient/PHOENIX/PROTECTED/PrescientME/raw/ME84344/mri/ME84344_MR_2023_03_03_1.zip'
    run_sheet = get_matching_run_sheet_path(data_loc, '2023_03_03_1')
    print(run_sheet)




