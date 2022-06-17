import os
from pathlib import Path
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, date, timedelta
from typing import List
import getpass
import subprocess
import pandas as pd
from pytz import timezone
import socket
from phantom_check.qqc.qqc_summary import qqc_summary, qqc_summary_detailed
tz = timezone('EST')

__dir__ = os.path.dirname(__file__)

def send(recipients, sender, subject, message, test, mailx, sender_pw):
    '''send an email'''
    # email_template = os.path.join(__dir__, 'bootdey_template.html')
    # with open(email_template, 'r') as fo:
        # template = string.Template(fo.read())
    # message = template.safe_substitute(message=str(message))
    # msg = MIMEText(message, 'html')
    # msg['Subject'] = subject
    # msg['From'] = sender
    # msg['To'] = ', '.join(recipients)
    # s = smtplib.SMTP('localhost')
    # s.sendmail(sender, recipients, msg.as_string())
    # s.quit()

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients[0]
    text = MIMEText(message, 'html')
    msg.attach(text)

    # image attachment
    # for image_path in image_paths:
        # with open(image_path, 'rb') as fp:
            # image_data = fp.read()
        # image = MIMEImage(image_data, name=image_path.name)
        # msg.attach(image)

    # send email
    if mailx:
        s = smtplib.SMTP('localhost')
    else:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(sender, sender_pw)

    if not test:
        s.sendmail(sender, recipients, msg.as_string())
        print('Email sent')
    else:
        print(message)

    s.quit()


def create_html_for_qqc(template, title: str, subtitle: str,
                        first_message:str, second_message: str,
                        code: str, in_mail_footer: str,
                        image_paths: List[str]):
    # information to be included in the email
    footer = 'If you see any error, please email kevincho@bwh.harvard.edu'
    html_str = template.render(title=title,
                               subtitle=subtitle,
                               first_message=first_message,
                               second_message=second_message,
                               code=code,
                               in_mail_footer=in_mail_footer,
                               footer=footer,
                               server=socket.gethostname(),
                               username=getpass.getuser(),
                               image_paths=image_paths)
    return html_str


def create_html_for_qqc_study(template, title: str, subtitle: str,
                              first_message:str, second_message: str,
                              code: str, in_mail_footer: str,
                              qqc_html_list: List[str]):
    # information to be included in the email
    footer = 'If you see any error, please email kevincho@bwh.harvard.edu'
    html_str = template.render(title=title,
                               subtitle=subtitle,
                               first_message=first_message,
                               second_message=second_message,
                               code=code,
                               in_mail_footer=in_mail_footer,
                               footer=footer,
                               server=socket.gethostname(),
                               username=getpass.getuser(),
                               qqc_html_list=qqc_html_list)
    return html_str


def send_detail(sender: str, recipients: List[str],
                title: str, subtitle: str, first_message: str,
                second_message: str, code: List[str],
                image_paths: list,
                qqc_html_list: list,
                in_mail_footer: str,
                qqc_out_dir: Path,
                test: bool = False,
                mailx: bool = True,
                sender_pw: str = None) -> None:
    '''Email Phantom check updates
    
    Key Arguments:
        sender: sender email address, str.

    This function uses Linux's mailx system by default. But when
    mailx = False, it uses Google's SMTP server to send emails.
    For the latter case, you will need to set up a
    Google account with "Less secure app access" turned on, from "Manage
    your Google account" page. Also, sender_pw needs to be provided.
    '''

    # get template
    env = Environment(loader=FileSystemLoader(str(__dir__)))

    # html form to be used for email
    email_template = env.get_template('bootdey_template_clean.html')
    html_str = create_html_for_qqc(email_template, title, subtitle,
            first_message, second_message, code, in_mail_footer,
            image_paths)
    send(recipients, sender, title, html_str, test, mailx, sender_pw)

    # html form to be saved in the server
    outloc = Path(qqc_out_dir) / 'qqc_summary.html'
    template = env.get_template('bootdey_template.html')
    html_str = create_html_for_qqc(template, title, subtitle,
            first_message, second_message, code, in_mail_footer,
            image_paths)
    with open(outloc, 'w') as fh:
        fh.write(html_str)

    # study level html
    study_template = env.get_template('bootdey_template_study.html')
    study_level_html = Path(qqc_out_dir).parent.parent / 'study_summary.html'
    html_str = create_html_for_qqc_study(template, title, subtitle,
            first_message, second_message, code, in_mail_footer,
            qqc_html_list)
    with open(study_level_html, 'w') as fh:
        fh.write(html_str)

def extract_info_for_qqc_report(qqc_out_dir: Path,
                                standard_dir: Path,
                                run_sheet_df: pd.DataFrame) -> tuple:
    '''Extract and clean up information from QQC for email

    Key arguments:
        qqc_out_dir: location of QQC output, Path.
        standard_dir: location of the template nifti directory (BIDS), Path.
        run_shee_df: run sheet loaded from PHOENIX, pd.DataFrame.


    Returns:
        A tuple containing
            - sender
            - recipients
            - title
            - subtitle
            - top_message: the messages to be included in the main container
            - qc_detail: detailed QC measures in the main container
            - code: TODO see if this could be removed
            - image_paths: list of image paths that are created by QQC
            - qqc_html_list: list of htmls created for the same study
            - in_mail_footer
    '''

    summary_df, protocol_df, other_dfs, titles = qqc_summary_detailed(
            qqc_out_dir)

    # get subject info
    session_name = qqc_out_dir.name.split('-')[1]
    subject_name = qqc_out_dir.parent.name.split('-')[1]

    # get data info
    mri_root = qqc_out_dir.parent.parent.parent.parent
    rawdata_root = mri_root / 'rawdata'
    rawdata_dir = rawdata_root / qqc_out_dir.parent.name / qqc_out_dir.name
    source_dir = mri_root / 'sourcedata' / subject_name / qqc_out_dir.name


    # extract extra information
    json_comp = qqc_out_dir / '04_json_comparison_log.csv'
    json_comp_df = pd.read_csv(json_comp)
    json_comp_df['num'] = json_comp_df.input_json.str.split(
            '.json').str[0].str[-1]

    # get list of paths for images
    image_paths = list(qqc_out_dir.glob('*.png'))

    # get list of qqc html summaries for the whole study
    qqc_html_files = list(qqc_out_dir.parent.parent.glob('*/*/*.html'))
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

        qqc_html_list.append(qqc_html_dict)

    # Basic information for email
    sender = 'kevincho@bwh.harvard.edu'
    admin_recipient = 'kc244@research.partners.org'
    user_id = getpass.getuser()
    recipients = [admin_recipient, f'{user_id}@research.partners.org']
    title = f'{subject_name} - MRI QQC'
    subtitle = 'Automatically created message ' \
               f'for {subject_name} ({session_name})'

    # top part of the main container
    str_tmp = '<h2>{0} data location</h2><code>{1}</code><br><br>'
    dicom_loc_str = str_tmp.format('Dicom', source_dir)
    nifti_loc_str = str_tmp.format('Nifti', rawdata_dir)
    std_data_loc = str_tmp.format('Template nifti', standard_dir)
    qc_data_loc = str_tmp.format('QQC', qqc_out_dir)

    # table part of the main container
    str_tmp = '<h2>{0}</h2>{1}<br><br>'
    quick_qc_summary = str_tmp.format(
        'Quick-QC Summary',
        summary_df.to_html(na_rep='', justify='center'))

    run_sheet_summary = str_tmp.format(
        'Run sheet',
        run_sheet_df.to_html(na_rep='', justify='center'))

    comparison_str = str_tmp.format(
        'Comparing series protocols to standard',
        protocol_df.to_html(na_rep='', justify='center'))

    top_message = dicom_loc_str + nifti_loc_str + std_data_loc + \
        qc_data_loc + quick_qc_summary + run_sheet_summary + comparison_str


    # second_message: QC detail of the container
    qc_detail_header = '<h2>Each QC output in more detail</h2>'
    str_tmp = '<h3>{0}</h3>{1}'
    qc_detail_content = '<br><br>'.join(
        [str_tmp.format(
            x,
            y.to_html(index=False, na_rep='', justify='center')
            ) for x, y in zip(titles, other_dfs)])
    qc_detail = qc_detail_header + qc_detail_content

    # footer in the main container
    str_tmp = '<h4>{0} </h4><code>{1}</code><br><br>'
    in_mail_footer = str_tmp.format('QQC ran on', datetime.now(tz).date())
    in_mail_footer += str_tmp.format('QQC ran by', getpass.getuser())
    in_mail_footer += str_tmp.format('QQC ran from', socket.gethostname())

    code = ['']

    return (sender, recipients, title, subtitle, top_message, qc_detail,
            code, image_paths, qqc_html_list, in_mail_footer)


def send_out_qqc_results(qqc_out_dir: Path,
                         standard_dir: Path,
                         run_sheet_df: pd.DataFrame,
                         test: bool = False,
                         mailx: bool = True):
    '''Send Quick QC summary'''
    sender, recipients, title, subtitle, top_message, qc_detail, \
                code, image_paths, qqc_html_list, in_mail_footer = \
        extract_info_for_qqc_report(qqc_out_dir, standard_dir, run_sheet_df)

    send_detail(sender, recipients, title, subtitle, top_message, qc_detail,
                code, image_paths, qqc_html_list, in_mail_footer,
                qqc_out_dir, test, mailx)



def attempts_error(Lochness, attempt):
    msg = '\n'.join(attempt.warnings)
    send(Lochness['admins'], Lochness['sender'], 'error report', msg)


def metadata_error(Lochness, message):
    send(Lochness['admins'], Lochness['sender'], 'bad metadata', message)

