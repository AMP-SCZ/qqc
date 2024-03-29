import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

def test_get_RA_for_QC():
    ra_dict = get_RA_for_QC()
    print(ra_dict)


def get_RA_for_QC(qc_database: Path = 'ra_qc_order.csv') -> dict:
    if Path(qc_database).is_file():
        df = pd.read_csv(qc_database, index_col=0)
    else:
        df = pd.DataFrame({
            'RA_name':['Omar', 'Simone', 'Nastia', 'Nick', 'Elana'],
            'RA_email_address': ['ojohn@bwh.harvard.edu',
                                 'sveale1@bwh.harvard.edu',
                                 'AHAIDAR@PARTNERS.ORG',
                                 'NKIM14@mgh.harvard.edu',
                                 'EKOTLER@mgh.harvard.edu'],
            'last_QCed': [False, False, False, False, True]})

    ra_qced_last = df[df.last_QCed]
    get_index = lambda x: -1 if x == 3 else x
    next_ra_index = get_index(ra_qced_last.index[0]) + 1
    ra_to_qc = df.loc[next_ra_index]

    # update db
    df['last_QCed'] = False
    df.loc[next_ra_index, 'last_QCed'] = True
    df.to_csv(qc_database)

    return ra_to_qc.to_dict()


def convert_AU_to_US_date(au_time: str) -> str:
    return datetime.strptime(au_time,
            '%d/%m/%Y %I:%M:%S %p').strftime(
            '%Y-%m-%d')

def add_days_to_str_date(date_str: str, days: int) -> str:
    return (datetime.strptime(
            date_str, '%Y-%m-%d') + timedelta(days=days)).strftime('%Y-%m-%d')



if __name__ == '__main__':
    test_get_RA_for_QC()




