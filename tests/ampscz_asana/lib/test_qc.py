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
  

  
  
  
  
import pandas as pd

def test_compare_dates():
    data = {
        'entry_date': ['2022_10_14', '2022_10_15', '2022-11-15'],
        'domain_type_missing': ['"Timepoint: baseline_arm_1 | Date: 2022-10-14 | clinical measures"',
                                '"Timepoint: month_3_arm_1 | Date: | digital biomarkers"',
                                '"Timepoint: month_6_arm_1 | Date: 2022-11-15 | clinical measures"'],
        'reason_for_missing_data': ['','',''],
        'domain_missing' : ['','',''],
        'comments':['','',''],
        'missing_data_form_complete':['','','']
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
    
