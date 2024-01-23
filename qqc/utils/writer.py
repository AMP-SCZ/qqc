import pandas as pd
from pathlib import Path


def write_df_to_derivatives(
        subject, session, df, title, mri_root: Path='/data/predict1/data_from_nda/MRI_ROOT'):
    qqc_out_path = Path(mri_root) / \
            f'derivatives/quick_qc/sub-{subject}/ses-{session}'
    assert qqc_out_path.is_dir()
    if not qqc_out_path.is_dir():
        qqc_out_path.mkdir(parent=True)

    df_out = qqc_out_path / f'{title}.csv'
    df.to_csv(df_out, index=False)

    print(df_out)


def test_write_df_to_derivatives():
    subject = 'BI02450'
    session = '202304111'
    df = pd.DataFrame({'test': ['test']})
    title = 'test'
    write_df_to_derivatives(subject, session, df, title)
