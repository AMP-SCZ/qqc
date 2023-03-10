# Checking Missing MRI Data 

## Steps 
### 1. Create a new Jupyter Notebook 
### 2. Access the path containing the relevant function 

import sys
sys.path.append('/data/predict1/home/kcho/software/AMPSCZ_pipeline')

### 3. Import the ampscz_asana directory and the get_run_sheet_df function

import ampscz_asana
from ampscz_asana.lib.qc import get_run_sheet_df

### 4. Add the file that will be checked to a path 

from pathlib import Path
pronet_phoenix_path = Path('/data/predict1/data_from_nda/Pronet/PHOENIX')

### 5. Call the get_run_sheet_df function to create a dataframe with the file in the path

df_pronet = get_run_sheet_df(pronet_phoenix_path)

### 6. Filter out subjects that are not missing MRI data 

missing_pronet_mri_df = df_pronet[~df_pronet['mri_data_exist']] 

### 7. Save as csv in the directory that you want to keep it in

missing_pronet_mri_df.to_csv('/_desired directory_/missing_pronet_mri_df.csv')


## Full Sample Code 


import sys
sys.path.append('/data/predict1/home/kcho/software/AMPSCZ_pipeline')
import ampscz_asana
from ampscz_asana.lib.qc import get_run_sheet_df
from pathlib import Path
pronet_phoenix_path = Path('/data/predict1/data_from_nda/Pronet/PHOENIX')
df_pronet = get_run_sheet_df(pronet_phoenix_path)
missing_pronet_mri_df = df_pronet[~df_pronet['mri_data_exist']]
missing_pronet_mri_df.to_csv('/_desired directory_/missing_pronet_mri_df.csv')




