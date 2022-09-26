import asana
import re
from pathlib import Path
from ampscz_asana.lib.server_scanner import consent_date_extraction, \
        consent_date_extraction_csv
from ampscz_asana.lib.utils import add_days_to_str_date
from typing import List


def read_token() -> str:
    '''Read Asana credentials'''
    token_loc = '/data/predict/kcho/software/asana_pipeline/data/.asana_token'
    with open(token_loc, 'r') as fp:
        token = fp.read().strip()

    return token


def get_all_task(client: 'asana.client',
                 project_gid: str) -> List['asana.task']:
    tasks = client.tasks.get_tasks_for_project(project_gid)
    return list(tasks)


def get_task_with_str(tasks: List['asana.task'],
                      potential_subject: str) -> 'asana.task':
    '''If returns None, no matching task'''
    for task in tasks:
        if task['name'] == potential_subject:
            return task

    return None


def get_all_subtask(client: 'asana.client',
                    task: 'asana.task') -> List['asana.task']:
    '''pass'''
    return list(client.tasks.get_subtasks_for_task(task['gid']))


def get_subtask_with_str(subtasks: List['asana.subtasks'],
                         name: str) -> 'asana.subtask':
    for subtask in subtasks:
        if name in subtask['name']:
            return subtask

    return None


def get_all_sections(client, project_gid):
    return list(client.sections.get_sections_for_project(project_gid))


def get_section_with_str(sections, name: str) -> 'asana.section':
    for section in sections:
        if name in section['name']:
            return section


def create_new_task(client: asana.client,
                    potential_subject: str,
                    subject_info_dict: dict,
                    ws_gid: str,
                    project_gid: str) -> 'asana.task':
    '''Creates new task and represents a new subject added to the server

    Note:
        subject_info_dict = {'consent_date': 'YYYY-MM-DD'}
    '''
    new_task = {
        'name': potential_subject,
        'note': 'New Data has been uploaded for ' + potential_subject,
        'assignee': 'kevincho@bwh.harvard.edu',
        'projects': [project_gid],
        'start_on': subject_info_dict['consent_date'],
        'due_on': subject_info_dict['end_date']
    }

    created_task = client.tasks.create_in_workspace(ws_gid, new_task)

    return created_task


'''def update_task_list(project_gid):
    tasks = client.tasks.ampscz_id(project_gid)
    tasks_list = list(tasks)
    print('Returning updated list of all tasks in AMP SCZ project')
    return tasks_list'''


def create_new_eeg_subtask(client: asana.client,
                           potential_subject: str,
                           ws_gid: str,
                           project_gid: str,
                           eeg_arrival_date: str,
                           eeg_due_date: str) -> 'asana.subtask':
    '''Creates new eeg subtask and links it to its parent task'''

    tasks = client.tasks.get_tasks_for_project(project_gid)
    tasks_list = list(tasks)
    for i in tasks_list:
        if i['name'] == potential_subject:
            parent_gid = i['gid']
    # loops through all tasks in AMP-SCZ project and assigns the correct
    # subject gid to be linked to the new eeg data

    # 'assignee': person responsible for doing EEG QC 
    new_eeg_subtask = {
        'name': 'EEG',
        'note': f'EEG data for {potential_subject} has arrived, please do QC!',
        'assignee': 'ojohn@bwh.harvard.edu',
        'projects': [project_gid],
        'start_on': eeg_arrival_date,
        'due_on': eeg_due_date,
        'parent': parent_gid}

    eeg_subtask = client.tasks.create_in_workspace(ws_gid, new_eeg_subtask)
    '''creates the subtask in asana'''

    qc_section_number = '1202669181415155'
    eeg_subtask_section = client.sections.add_task_for_section(
            qc_section_number,
            {'task': eeg_subtask['gid']})
    # moves the subtask to Data QC section in AMP-SCZ project'''

    eeg_subtask_dependent = client.tasks.add_dependents_for_task(
            parent_gid,
            {'dependents': eeg_subtask['gid']})
    # links the eeg subtask to its parent task as a dependent

    return eeg_subtask


def create_new_subtask(client: asana.client,
                       potential_subject: str,
                       ws_gid: str,
                       project_gid: str,
                       data_type: str,
                       section_name: str,
                       data_arrival_date: str,
                       qc_due_date: str,
                       phoenix_dir: Path) -> 'asana.subtask':
    '''Creates new eeg subtask and links it to its parent task'''
    tasks = client.tasks.get_tasks_for_project(project_gid)
    tasks_list = list(tasks)
    parent_gid = ''
    for i in tasks_list:
        if i['name'] == potential_subject:
            parent_gid = i['gid']

    if parent_gid == '':
        # if pronet
        if 'Pronet' in str(phoenix_dir):
            consent_date = consent_date_extraction(potential_subject,
                                                   phoenix_dir)
        else:
            consent_date = consent_date_extraction_csv(potential_subject,
                                                       phoenix_dir)
        consent_date = re.sub('_', '-', consent_date)
        subject_info_dict = {
                'consent_date': consent_date,
                'end_date': add_days_to_str_date(consent_date, 3)}

        print(subject_info_dict)
        subject_task = create_new_task(client, potential_subject,
                subject_info_dict, ws_gid, project_gid)
        parent_gid = subject_task['gid']
    # loops through all tasks in AMP-SCZ project and assigns the correct
    # subject gid to be linked to the new eeg data

    # 'assignee': person responsible for doing EEG QC 
        # 'assignee': 'ojohn@bwh.harvard.edu',
    new_subtask = {
        'name': data_type,
        'note': f'{data_type} data for {potential_subject}',
        'projects': [project_gid],
        'start_on': data_arrival_date,
        'due_on': qc_due_date,
        'parent': parent_gid}

    # creates the subtask in asana
    subtask = client.tasks.create_in_workspace(ws_gid, new_subtask)

    for section in client.sections.get_sections_for_project(project_gid):
        if 'Run sheet' in section['name']:
            # qc_section_number = '1202669181415155'
            qc_section_number = section['gid']

    # moves the subtask to Data QC section in AMP-SCZ project'''
    sections = get_all_sections(client, project_gid)
    subtask_section = get_section_with_str(sections, section_name)
    client.sections.add_task_for_section(
            subtask_section['gid'],
            {'task': subtask['gid']})

    subtask_dependent = client.tasks.add_dependents_for_task(
            subtask['gid'],
            {'dependents': parent_gid})
    # links the subtask to its parent task as a dependent

    return subtask



def get_asana_ready(project_name='AMP SCZ') -> tuple:
    token = read_token()
    client = asana.Client.access_token(token)

    workspace_gid = next(client.workspaces.get_workspaces())['gid']
    projects = client.projects.get_projects_for_workspace(workspace_gid)
    for project in projects:
        if project['name'] == project_name:
            project_gid = project['gid']

    return client, workspace_gid, project_gid

if __name__ == '__main__':

    client, workspace_gid, project_gid = get_asana_ready()
    create_new_task('test', workspace_gid, project_gid)

    # amp_scz = client.projects.get_project(project_gid)
    # amp_scz_gid = amp_scz['gid']
    #update_task_list())['gid']
