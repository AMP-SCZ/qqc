from ampscz_asana.lib.qc import date_of_zip, extract_variable_information, extract_missing_data_information, compare_dates


def test_date_of_zip():
  dir = '/data/predict1/data_from_nda/Pronet/PHOENIX'
  
  assert(date_of_zip('TE00307', '2022_10_20', dir)) == '2022-11-12'
  assert(date_of_zip('LA07315', '2022_12_16', dir)) == '2022-12-17'

  
  dir = '/data/predict1/data_from_nda/Prescient/PHOENIX'

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
            "'Timepoint: month_3_arm_1 | Date: | Other reason', 'Timepoint: baseline_arm_1 | Date: 2022-10-14 | Other reason'")
  except AssertionError:
    print("Assertion failed!")
  

  
  
  
  
#def test_compare_dates():
