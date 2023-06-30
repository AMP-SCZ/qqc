import subprocess
import sys
from pathlib import Path

data_flow_dir = Path('/data/predict1/data_from_nda')
MRI_ROOT = data_flow_dir / 'MRI_ROOT'
job_dir = MRI_ROOT / 'jobs'

for study_network in ['Prescient', 'Pronet']:
    PHOENIX_DIR = data_flow_dir / study_network / 'PHOENIX'
    for i in Path(PHOENIX_DIR / 'PROTECTED').glob('*/raw/*/mri/*_MR_*_[1234].[zZ][iI][pP]'):
        filepath = str(i)

        if filepath in Path('/data/predict1/data_from_nda/MRI_ROOT/codes/data_to_ignore.txt').read_text().splitlines():
            continue

        print(f"reviewing {filepath} ...")
        mri_dirname = i.name
        subject = mri_dirname.split('_')[0]
        year, month, day, dup = mri_dirname.split('_')[2:6]
        year, month, day, dup = year[:4], month, day, dup[0]

        session = f"{year}_{month.zfill(2)}_{day.zfill(2)}_{dup}"
        session_wo = f"{year}{month.zfill(2)}{day.zfill(2)}{dup}"

        qqc_summary_html_file = MRI_ROOT / 'derivatives' / 'quick_qc' / f'sub-{subject}' / f'ses-{session_wo}' / 'qqc_summary.html'
        if not qqc_summary_html_file.exists():
            print(qqc_summary_html_file)
            print("=========================")
            print("QQC is not complete for")
            print(f"zipfile- {filepath}")
            print(f"subject- {subject}")
            print(f"session- {session}")
            print(f"{qqc_summary_html_file} is missing")

            # Replace the following command with the appropriate Python code for executing dicom_to_dpacc_bids.py
            python_cmd = [
                '/data/pnl/kcho/anaconda3/bin/python',
                '/data/predict1/home/kcho/software/qqc/scripts/dicom_to_dpacc_bids.py',
                '-i', filepath,
                '-s', subject,
                '-ss', session,
                '-o', str(MRI_ROOT),
                '--email_report',
                '--config', '/data/predict1/data_from_nda/MRI_ROOT/standard_templates.cfg',
                '--force_heudiconv',
                '--dwipreproc', '--mriqc', '--fmriprep',
                '--additional_recipients',
                'kc244@research.partners.org',
                'oj026@research.partners.org',
                'op7@research.partners.org',
                'ah314@research.partners.org',
                'ebk17@research.partners.org',
                'nk582@research.partners.org',
                'lning@bwh.harvard.edu',
                'SFADNAVIS@mgh.harvard.edu',
                'ob001@mgh.harvard.edu',
                'awickham3@mgh.harvard.edu',
            ]

            print(python_cmd)
            subprocess.run(python_cmd)
            print("=========================")
            print()

