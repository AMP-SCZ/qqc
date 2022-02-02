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
from phantom_check.qqc.qqc_summary import qqc_summary
tz = timezone('EST')

__dir__ = os.path.dirname(__file__)

def send(recipients, sender, subject, message):
    '''send an email'''
    email_template = os.path.join(__dir__, 'template.html')
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
    msg['Subject'] = f'Lochness update {datetime.now(tz).date()}'
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
                         test: bool = False,
                         mailx: bool = True):
    '''Send Quick QC summary'''

    summary_df = qqc_summary(qqc_out_dir)

    send_detail(
        'kevincho@bwh.harvard.edu',
        ['kevincho@bwh.harvard.edu'],
        'Quick QC Summary', f'{datetime.now(tz).date()}',
        'Summary of files sent to NDA' + summary_df.to_html(),
        'Each file in detail',
        [''],
        'tmp version',
        test, mailx)

        # 'Each file in detail' + s3_df_selected.to_html(),
        # list_of_lines_from_tree,
        # in_mail_footer,
        # test, mailx)


    # s3_log = Path(Lochness['phoenix_root']) / 's3_log.csv'
    # if s3_log.is_file():
        # s3_df = pd.read_csv(s3_log)
        # s3_df['timestamp'] = pd.to_datetime(s3_df['timestamp'])
        # s3_df['ctime'] = pd.to_datetime(s3_df['ctime']).apply(
                # lambda x: x.replace(microsecond=0))

        # # get the timestamp to check the dataflow from
        # date_to_check_from = datetime.now(tz).date() - timedelta(days=days-1)
        # timestamp_to_check_from = pd.Timestamp(date_to_check_from)

        # s3_df_selected = s3_df[s3_df['timestamp'] > timestamp_to_check_from]

        # s3_df_selected = s3_df_selected.fillna('_')

        # s3_df_selected = s3_df_selected[~s3_df_selected.filename.str.contains(
            # 'metadata.csv')][['timestamp', 'filename', 'protected', 'study',
                              # 'processed', 'subject', 'datatypes', 'ctime']]

        # s3_df_selected['date'] = s3_df_selected['timestamp'].apply(
                # lambda x: x.date())
        # count_df = s3_df_selected.groupby([
            # 'date', 'protected', 'study',
            # 'processed', 'subject', 'datatypes']).count()[['filename']]
        # count_df.columns = ['file count']
        # count_df = count_df.reset_index()
        # s3_df_selected.drop('date', axis=1, inplace=True)

    # else:
        # s3_df_selected = pd.DataFrame()
        # count_df = pd.DataFrame()

    # list_of_lines_from_tree = ['']

    # day_days = 'days' if days > 1 else 'day'

    # if len(s3_df_selected) == 0:
        # send_detail(
            # Lochness,
            # 'Lochness', f'Daily updates {datetime.now(tz).date()}',
            # 'There is no update!', '',
            # list_of_lines_from_tree,
            # '',
            # test, mailx)
    # else:
        # s3_df_selected.columns = ['Transfer time (UTC)', 'File name',
                                  # 'Protected', 'Study', 'Processed', 'Subject',
                                  # 'Datatype', 'Download time (UTC)']
        # s3_df_selected.reset_index().drop('index', axis=1, inplace=True)

        # # too many dicom file names -> remove
        # subject_mri_gb = s3_df_selected[
                # s3_df_selected.Datatype == 'mri'].groupby('subject')

        # sample_mri_df = pd.DataFrame()
        # for _, table in subject_mri_gb:
            # subject_mri_sample = table.iloc[:2]  # select only two raws
            # subject_mri_sample.iloc[1]['File name'] = '...'
            # sample_mri_df = pd.concat([sample_mri_df, subject_mri_sample])

        # s3_df_selected = pd.concat([
            # s3_df_selected[s3_df_selected.Datatype != 'mri'],
            # sample_mri_df]).sort_index()

        # in_mail_footer = 'Note that only S3 transferred files are included.'

        # send_detail(
            # Lochness,
            # 'Lochness', f'Daily updates {datetime.now(tz).date()} '
                        # f'(for the past {days} {day_days})',
            # 'Summary of files sent to NDA' + count_df.to_html(),
            # 'Each file in detail' + s3_df_selected.to_html(),
            # list_of_lines_from_tree,
            # in_mail_footer,
            # test, mailx)


def attempts_error(Lochness, attempt):
    msg = '\n'.join(attempt.warnings)
    send(Lochness['admins'], Lochness['sender'], 'error report', msg)


def metadata_error(Lochness, message):
    send(Lochness['admins'], Lochness['sender'], 'bad metadata', message)

