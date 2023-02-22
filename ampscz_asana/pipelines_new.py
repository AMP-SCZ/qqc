import pandas as pd
import sys
from pathlib import Path
import re
from datetime import datetime, timedelta
from ampscz_asana.lib.asana_api import get_asana_ready, get_all_task, \
        get_task_with_str, get_all_subtask, create_new_subtask, \
        get_subtask_with_str
from ampscz_asana.lib.qc import get_run_sheet_df
from ampscz_asana.lib.utils import add_days_to_str_date


def mri_asana_pipeline(phoenix_dir: Path) -> None:
    '''Run MRI pipeline through Asana'''
    client, workspace_gid, project_gid = get_asana_ready(
        project_name='AMP-SCZ MRI dataflow & QC')
    run_sheet_df = get_run_sheet_df(phoenix_dir)
    run_sheet_df.to_csv('tmp.csv')

    tasks = get_all_task(client, project_gid)
    today_date_string = datetime.today().strftime('%Y-%m-%d')
    tomorrow_date_string = (
            timedelta(days=1) + datetime.today()
        ).strftime('%Y-%m-%d')

    for _, row in run_sheet_df.iterrows():
        entry_date_numbers_only = re.sub('_', '-', row.entry_date)
        if entry_date_numbers_only == '':
            print('\nNo proper entry date on REDCap run sheet')
            print('\nList of files')
            for i in row.file_path.parent.glob('*'):
                print(f'\t\tt{i.name}')
            continue

        ###############################################################
        # Subject
        ###############################################################
        print(f'Going through subject {row.subject} {row.entry_date}')
        # task is for subject ID
        task = get_task_with_str(tasks, row.subject)

        if task is None:
            print('\tNew subject')
            print(task)
            print(tasks)
            task = client.tasks.create_in_workspace(
                workspace_gid,
                {'name': row.subject,
                 'note': 'New Data has been uploaded for ' + row.subject,
                 'assignee': 'kevincho@bwh.harvard.edu',
                 'projects': [project_gid],
                 'start_on': entry_date_numbers_only,
                 'due_on': add_days_to_str_date(entry_date_numbers_only, 7)})


        ###############################################################
        # Session date
        ###############################################################
        # here we need to catch session date task (entry_date)
        # subtasks = get_all_subtask(client, task)
        print(f'\tChecking if {row.subject} have MRI data')
        session_name = f'{row.subject}-{row.entry_date}'
        session_task = get_task_with_str(tasks, session_name)

        # if run sheet exists, but no MRI data
        # if not row.mri_data_exist:  # no MRI data
        # session_task = get_subtask_with_str(subtasks, session_name)
        section_name = 'Session date'
        if session_task is None:  # if doesn't exist
            if pd.isna(row.mri_arrival_date):
                try:
                    session_task = create_new_subtask(
                        client, row.subject, workspace_gid, project_gid,
                        session_name,
                        section_name,
                        entry_date_numbers_only,
                        today_date_string,
                        phoenix_dir)
                except:
                    session_task = create_new_subtask(
                        client, row.subject, workspace_gid, project_gid,
                        session_name,
                        section_name,
                        entry_date_numbers_only,
                        add_days_to_str_date(today_date_string, 1),
                        phoenix_dir)
            else:
                session_task = create_new_subtask(
                    client, row.subject, workspace_gid, project_gid,
                    session_name,
                    section_name,
                    entry_date_numbers_only,
                    row.mri_arrival_date,
                    phoenix_dir)
        else:  # if it exist, update the 'due_on'
            print(row)
            print(row.mri_arrival_date)
            client.tasks.update_task(
                session_task['gid'],
                {'due_on': row.mri_arrival_date})


        ###############################################################
        section_name = 'Run sheet scan date'
        ###############################################################
        subtasks = get_all_subtask(client, session_task)
        if not row.mri_data_exist:  # no MRI data
            subtask_name = 'Run sheet exists but no MRI yet'
            subtask = get_subtask_with_str(subtasks, subtask_name)
            if subtask is None:  # if doesn't exist
                create_new_subtask(
                    client, session_name, workspace_gid, project_gid,
                    subtask_name,
                    section_name,
                    entry_date_numbers_only,
                    tomorrow_date_string,
                    phoenix_dir)
            else:  # if it exist, update the 'due_on'
                client.tasks.update_task(
                    subtask['gid'],
                    {'due_on': tomorrow_date_string})
        else:  # MRI data exists
            # if there is now MRI data, complete the task
            subtask_name = 'Run sheet exists but no MRI yet'
            subtask = get_subtask_with_str(subtasks, subtask_name)
            if subtask is not None:
                result = client.tasks.get_task(subtask['gid'])
                if result['due_on'] == row.mri_arrival_date:
                    pass
                else:
                    client.tasks.update_task(
                            subtask['gid'],
                            {'due_on':row.mri_arrival_date,
                             'completed': True})
            else:
                subtask = create_new_subtask(
                    client, session_name, workspace_gid, project_gid,
                    subtask_name,
                    section_name,
                    entry_date_numbers_only,
                    tomorrow_date_string,
                    phoenix_dir)
                client.tasks.update_task(
                        subtask['gid'],
                        {'due_on':row.mri_arrival_date,
                         'completed': True})

            # Manual QC
            subtask_name = 'Manual QC'
            subtask = get_subtask_with_str(subtasks, subtask_name)
            section_name = 'Manual QC'
            if subtask is None:
                create_new_subtask(
                    client, session_name, workspace_gid, project_gid,
                    subtask_name,
                    section_name,
                    entry_date_numbers_only,
                    add_days_to_str_date(entry_date_numbers_only, 3),
                    phoenix_dir)

            # Automatic QC
            subtask_names = ['QQC', 'fMRIPrep',
                             'MRIQC', 'DWI preprocessing']
            table_columns = ['qqc_executed', 'fmriprep_done',
                             'mriqc_done', 'dwipreproc_done']
            for subtask_name, col in zip(subtask_names, table_columns):
                print(f'\tChecking if {row.subject} {session_name} have {subtask_name} '
                      'subtask')
                # get matching subtask
                subtask = get_subtask_with_str(subtasks, subtask_name)
                section_name = 'Automatic QC'

                if not row[col]:  # if not done
                    if subtask is None:  # create subtask if doesn't exist
                        create_new_subtask(
                            client, session_name, workspace_gid, project_gid,
                            subtask_name,
                            section_name,
                            entry_date_numbers_only,
                            add_days_to_str_date(entry_date_numbers_only, 3),
                            phoenix_dir)
                    else:
                        client.tasks.update_task(subtask['gid'],
                                                 {'completed': False})

                else:  # if done
                    if subtask is not None:
                        if 'completed' in subtask:
                            if not subtask['completed']:
                                client.tasks.update_task(subtask['gid'],
                                                         {'completed': True})
                        else:
                            client.tasks.update_task(subtask['gid'],
                                                     {'completed': True})
                    else:
                        subtask = create_new_subtask(
                            client, session_name, workspace_gid, project_gid,
                            subtask_name,
                            section_name,
                            entry_date_numbers_only,
                            add_days_to_str_date(entry_date_numbers_only, 3),
                            phoenix_dir)
                        client.tasks.update_task(subtask['gid'],
                                                 {'completed': True})


