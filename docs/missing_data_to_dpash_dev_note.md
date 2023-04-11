# `missing_data` search to DPDash development notes


## Contents

1. Background
2. Steps
3. Test


## Background

Simone and Omar initiated a project to visualize AMP-SCZ MRI data flow from each network to DPACC. Owen has further improved the tool
to include the timestamp of each data trasfer. Now the output dataframe needs to be cleaned up and imported into DPDash.


## Steps

1. Find out the most recent branch that has Owen's update.
2. Newly clone `QQC` to a local directory and checkout to this branch

```sh
git clone https://github.com/AMP-SCZ/qqc
cd qqc
git checkout pnldev
```

3. Add this newly pulled `qqc` to the `PYTHONPATH` in the shell.

```sh
export PYTHONPATH=${PWD}:${PYTHONPATH}
```

4. Find Owen's test function and try running the function to check his latest updates are running on my environment

```sh

cd tests/ampscz_asana/lib
pytest test_qc.py -s
```

5. Once Owen's test functions are checked, create a new test function that creates_the correct DPDash table.

```sh
vi test_qc.py
```

```py
from ampscz_asana.lib.qc import get_run_sheet_df

def test_dpdash_output():
    phoenix_root = '/data/to/phoenix'
    df = get_run_sheet_df(phoenix_root)
    print(df)
```

Save and run this test by and check the output on the shell

```sh
pytest test_qc.py -s -k test_dpdash_output
```


### The dataframe is too long and wide to visualize effectively in the terminal. Select columns to print.

> edit test_qc.py and rerun pytest to print name of columns

```py
print(df.columns)
```

> edit test_qc.py to selectively print the columns in interest

```py
# edit test_qc.py and rerun
cols_to_print = ['file_path',
                 'subject',
                 'other_files',
                 'entry_date',
                 'mri_data_exist',
                 'mri_arrival_date',
                 'qqc_date']

print(run_sheet_df[cols_to_print].head())
```

