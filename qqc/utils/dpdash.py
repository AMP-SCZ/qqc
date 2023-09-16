import re
import pandas as pd
from pathlib import Path
from datetime import datetime

FORMSQC_ROOT = Path('/data/predict1/data_from_nda/formqc')


def get_most_recent_formsqc_summary(forms_root: Path = FORMSQC_ROOT) -> Path:
    """Get most recent AMP-SCZ forms-QC summary csv path"""
    summary_csvs = Path(forms_root).glob('Summary_AMP-SCZ_forms_*.csv')

    most_recent_date = datetime.strptime('1900-01-01', '%Y-%m-%d')
    most_recent_csv = ''
    for summary_csv in summary_csvs:
        date_str = re.search(r'\d{4}-\d{2}-\d{2}', summary_csv.name).group(0)
        date = datetime.strptime(date_str, '%Y-%m-%d')
        if most_recent_date < date:
            most_recent_date = date
            most_recent_csv = summary_csv

    return most_recent_csv


def get_summary_included_ids(forms_root: Path = FORMSQC_ROOT) -> list:
    forms_summary_csv = get_most_recent_formsqc_summary()
    return pd.read_csv(forms_summary_csv).subjectid.unique()


def test_get_most_recent_formsqc_summary():
    get_most_recent_formsqc_summary()


def test_get_summary_included_ids():
    get_summary_included_ids()

