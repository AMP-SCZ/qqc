from phantom_check.email import send_out_qqc_results, send
from pathlib import Path
import pandas as pd
import os
pd.set_option('max_rows', 5000)


def test_format():
    from jinja2 import Environment, FileSystemLoader
    import phantom_check
    email_template_dir = os.path.join(Path(phantom_check.email.__dir__))
    print(email_template_dir)
    from email.mime.text import MIMEText

    env = Environment(loader=FileSystemLoader(str(email_template_dir)))
    template = env.get_template('bootdey_template.html')
    html_str = template.render()
    import smtplib
    
    with open('test.html', 'w') as f:
        f.write(html_str)

    msg = MIMEText(html_str, 'html')
    msg['Subject'] = 'test_title'
    msg['From'] = 'kevincho@bwh.harvard.edu'
    msg['To'] = 'kevincho@bwh.harvard.edu'

    s = smtplib.SMTP('localhost')
    s.sendmail('kevincho@bwh.harvard.edu', 'kevincho@bwh.harvard.edu', msg.as_string())
    
def test_send_out_qqc_results():
    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-NL00000/ses-202112071'
    
    # send_out_qqc_results(qqc_out_dir, test=True)
    send_out_qqc_results(qqc_out_dir)

    # send(['kevincho@bwh.harvard.edu'], 'kc244@research.partners.org', 'ha', 'ho')
