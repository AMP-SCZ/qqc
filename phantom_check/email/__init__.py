import os
from pathlib import Path
import string
import smtplib
from email.mime.text import MIMEText
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

def send(recipients, sender, subject, message):
    '''send an email'''
    email_template = os.path.join(__dir__, 'bootdey_template.html')
    with open(email_template, 'r') as fo:
        template = string.Template(fo.read())
    message = template.safe_substitute(message=str(message))
    msg = MIMEText(message, 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    s = smtplib.SMTP('localhost')
    s.sendmail(sender, recipients, msg.as_string())
    s.quit()


def send_detail(sender: str, recipients: List[str],
                title: str, subtitle: str, first_message: str,
                second_message: str, code: List[str],
                in_mail_footer: str,
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

    email_template_dir = os.path.join(__dir__)
    env = Environment(loader=FileSystemLoader(str(email_template_dir)))
    template = env.get_template('bootdey_template.html')
    footer = 'If you see any error, please email kevincho@bwh.harvard.edu'
    server_name = socket.gethostname()

    html_str = template.render(title=title,
                               subtitle=subtitle,
                               first_message=first_message,
                               second_message=second_message,
                               code=code,
                               in_mail_footer=in_mail_footer,
                               footer=footer,
                               server=server_name,
                               username=getpass.getuser())

    msg = MIMEText(html_str, 'html')
    msg['Subject'] = title
    msg['From'] = sender
    msg['To'] = recipients[0]

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
        print(html_str)

    s.quit()


def send_out_qqc_results(qqc_out_dir: Path,
                         standard_dir: Path,
                         test: bool = False,
                         mailx: bool = True):
    '''Send Quick QC summary'''
    # get subject info
    session_name = qqc_out_dir.name.split('-')[1]
    subject_name = qqc_out_dir.parent.name.split('-')[1]

    rawdata_dir = qqc_out_dir.parent.parent.parent.parent / 'rawdata' / \
        qqc_out_dir.parent.name / qqc_out_dir.name

    source_dir = qqc_out_dir.parent.parent.parent.parent / 'sourcedata' / \
        subject_name / qqc_out_dir.name

    summary_df, protocol_df, other_dfs, titles = qqc_summary_detailed(qqc_out_dir)

    # extract extra information
    json_comp = qqc_out_dir / '04_json_comparison_log.csv'
    json_comp_df = pd.read_csv(json_comp)
    json_comp_df['num'] = json_comp_df.input_json.str.split(
            '.json').str[0].str[-1]

    send_detail(
        'kevincho@bwh.harvard.edu',
        ['kc244@research.partners.org'],
        f'{subject_name} - MRI QQC',
        f'Automatically created message for {subject_name} ({session_name})',
        f'<h2>Dicom data location</h2><code>{source_dir}</code><br><br>'
        f'<h2>Nifti data location</h2><code>{rawdata_dir}</code><br><br>'
        f'<h2>Standard BIDS session used to compare this data to</h2><code>{standard_dir}</code><br><br>'
        f'<h2>Full Quick QC output location</h2><code>{qqc_out_dir}</code><br><br>'
        '<h2>Quick-QC Summary</h2>' + summary_df.to_html(na_rep='', justify='center') + '<br><br>'
        '<h2>Comparing series protocols to standard</h2>' + protocol_df.to_html(na_rep='', justify='center') + '<br><br>',
        '<h2>Each QC output in more detail</h2>' + '<br><br>'.join([f'<h3>{x}</h3>'+ y.to_html(index=False, na_rep='', justify='center') for x, y in zip(titles, other_dfs)]),
        [''],
        f'<h4>QQC ran on </h2><code>{datetime.now(tz).date()}</code><br><br>'
        f'<h4>QQC ran by </h2><code>{getpass.getuser()}</code><br><br>'
        f'<h4>Command executed on</h2><code>{socket.gethostname()}</code><br><br>',
        test, mailx)



def attempts_error(Lochness, attempt):
    msg = '\n'.join(attempt.warnings)
    send(Lochness['admins'], Lochness['sender'], 'error report', msg)


def metadata_error(Lochness, message):
    send(Lochness['admins'], Lochness['sender'], 'bad metadata', message)

