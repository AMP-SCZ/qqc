from phantom_check.email import send_out_qqc_results, send, send_error
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
    from email.mime.image import MIMEImage

    env = Environment(loader=FileSystemLoader(str(email_template_dir)))
    template = env.get_template('bootdey_template.html')
    html_str = template.render()
    import smtplib
    

    attachment = '/data/predict/kcho/flow_test/MRI_ROOT/derivatives/quick_qc/sub-NL00000/ses-202112071/07_summary_b0.png'

    with open('test.html', 'w') as f:
        f.write(html_str)

    from email.mime.multipart import MIMEMultipart

    # msg = MIMEText(html_str, 'html')
    msg = MIMEMultipart()

    msg['Subject'] = 'test_title'
    msg['From'] = 'kevincho@bwh.harvard.edu'
    # msg['To'] = 'kevincho@bwh.harvard.edu'
    msg['To'] = 'kc244@research.partners.org'

    s = smtplib.SMTP('localhost')

    # from email.utils import make_msgid

    # attachment_cid = make_msgid()
    # msg.set_content(f'<img src="cid:{attachment_cid[1:-1]}"/>')
    with open(attachment, 'rb') as fp:
        img = MIMEImage(fp.read())

    img.add_header('Content-ID', f'<{attachment}>')
    msg.attach(img)
        # msg.add_related(fp.read(), 'image', 'png', cid=attachment_cid)

    s.sendmail('kevincho@bwh.harvard.edu', 'kc244@research.partners.org', msg.as_string())
    
def test_send_out_qqc_results():
    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-NL00000/ses-202112071'

    
    root_dir = Path('/data/predict/kcho/flow_test/MRI_ROOT')
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-ME00005/ses-202112081'
    print()
    print(qqc_out_dir)

    standard_dir = '/data/predict/phantom_human_pilot/rawdata/sub-ProNETUCLA/ses-humanpilot'
    # send_out_qqc_results(qqc_out_dir, test=True)
    send_out_qqc_results(qqc_out_dir, standard_dir, mailx=True)

    # send(['kevincho@bwh.harvard.edu'], 'kc244@research.partners.org', 'ha', 'ho')

def test_send_error():
    send_error('title', 'subtitle', 'top_message', 'second message')
