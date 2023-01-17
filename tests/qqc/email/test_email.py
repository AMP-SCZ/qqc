from qqc.email import send_out_qqc_results, send, send_error, \
        create_html_for_qqc_study
from pathlib import Path
import pandas as pd
import os
pd.set_option('max_rows', 5000)


def test_format():
    from jinja2 import Environment, FileSystemLoader
    import qqc
    email_template_dir = os.path.join(Path(qqc.email.__dir__))
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

def test_redcap_update_send_out_qqc_results():
    root_dir = Path('/data/predict/data_from_nda/MRI_ROOT')
    qqc_out_dir = root_dir / 'derivatives/quick_qc/sub-YA03473/ses-202211281'

    
    print()
    print(qqc_out_dir)

    standard_dir = '/data/predict/data_from_nda/MRI_ROOT/rawdata/sub-YA01508/ses-202206231'
    # send_out_qqc_results(qqc_out_dir, test=True)
    from qqc.run_sheet import get_run_sheet
    input_dir = Path('/data/predict/data_from_nda/Pronet/PHOENIX/PROTECTED/PronetYA/raw/YA03473/mri')
    run_sheet = next(input_dir.glob('*Run_sheet_mri*2*.csv'))
    run_sheet_df = get_run_sheet(run_sheet)
    send_out_qqc_results(qqc_out_dir, standard_dir, run_sheet_df, [], mailx=True)

def test_send_error():
    send_error('title', 'subtitle', 'top_message', 'second message')


def test_study_website():
    import qqc
    from jinja2 import Environment, FileSystemLoader
    email_template_dir = os.path.join(Path(qqc.email.__file__).parent)
    env = Environment(loader=FileSystemLoader(str(email_template_dir)))
    template = env.get_template('bootdey_template_study.html')
    title = '**title**'
    subtitle = '**subtitle**'
    first_message = '**first message**'
    second_message = '**second message**'
    code = ['**code1**', '**code2**']
    in_mail_footer = '*footer*'


    qqc_out_dir = Path('/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc')
    qqc_html_files = list(qqc_out_dir.glob('*/*/*.html'))
    qqc_html_list = []
    for qqc_html in qqc_html_files:
        qqc_html_dict = {}
        qqc_html_dict['subject_name'] = qqc_html.parent.parent.name
        qqc_html_dict['session_name'] = qqc_html.parent.name
        qqc_html_dict['qqc_html'] = qqc_html

        # qc
        qqc_html_dict['qc'] = 'Fail'
        if (qqc_html.parent / '00_qc_summary.csv').is_file():
            qc_summary_df = pd.read_csv(qqc_html.parent / '00_qc_summary.csv')
            col_name = qc_summary_df.columns[1]
            if (qc_summary_df.iloc[:6][col_name] == 'Pass').all():
                qqc_html_dict['qc'] = 'Pass'

    html_str = create_html_for_qqc_study(template, title, subtitle,
            first_message, second_message, code, in_mail_footer,
            qqc_html_list)

    with open('study_level.html', 'w') as fh:
        fh.write(html_str)
