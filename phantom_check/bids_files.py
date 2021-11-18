from pathlib import Path
import json
import os
import pandas as pd


def jsons_from_bids_to_df(session_dir: Path) -> pd.DataFrame:
    '''Read all json files from session_dir and return protocol name as df

    Key Argument:
        session_dir: root of session directory in BIDS format, Path.

    Returns:
        pd.DataFrame
    '''

    df = pd.DataFrame()
    num = 0
    for root, dirs, files in os.walk(session_dir):
        for file in files:
            if file.endswith('json'):
                with open(Path(root, file), 'r') as json_file:
                    data = json.load(json_file)
                    series_num = data['SeriesNumber']
                    series_desc = data['SeriesDescription']
                    df.loc[num, 'series_num'] = series_num
                    df.loc[num, 'series_desc'] = series_desc
                    num += 1

    return df

