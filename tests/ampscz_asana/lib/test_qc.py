from qqc.ampscz_asana.lib import date_of_zip


def test_date_of_zip():
  dir = '/data/predict1/data_from_nda/Pronet/PHOENIX'
  
  assert(date_of_zip('TE00307', '2022_10_20', dir)) == '2022-11-12'
  assert(date_of_zip('LA07315', '2022_12_16', dir)) == '2022-12-17'

  
  dir = '/data/predict1/data_from_nda/Prescient/PHOENIX'

  assert(date_of_zip('ME04934', '2022_12_02', dir)) == '2023-03-13'
  assert(date_of_zip('CP01128', '2023_02_23', dir)) == '2023-03-02
'
         
         

  
