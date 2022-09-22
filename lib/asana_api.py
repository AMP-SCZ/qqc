import asana
from pathlib import Path


def read_token() -> str:
    '''Read Asana credentials'''
    token_loc = '/data/predict/kcho/software/asana_pipeline/data/.asana_token'
    with open(token_loc, 'r') as fp:
        token = fp.read().strip()

    return token


def create_new_task(client: asana.client,
                    potential_subject: str,
                    subject_info_dict: dict,
                    ws_gid: str,
                    project_gid: str) -> 'asana.task':
    '''Creates new task to send to AMP-SCZ project in Asana and represents a new subject added to the server 

    Note:
        subject_info_dict = {'consent_date': 'YYYY-MM-DD'}

    '''
    new_task = {
        'name': potential_subject,
        'note': 'New Data has been uploaded for ' + potential_subject,
        'assignee': 'kevincho@bwh.harvard.edu',
        'projects': [project_gid],
        'start_on': subject_info_dict['consent_date']}

    created_task = client.tasks.create_in_workspace(ws_gid, new_task)

    return created_task


'''def update_task_list(project_gid):
    tasks = client.tasks.get_tasks_for_project(project_gid)
    tasks_list = list(tasks)
    print('Returning updated list of all tasks in AMP SCZ project')
    return tasks_list'''


def create_new_eeg_subtask(client: asana.client,
                           potential_subject: str,
                           ws_gid: str,
                           project_gid: str,
                           eeg_arrival_date: str):
    '''Creates new eeg subtask to send to AMP-SCZ project in Asana and links it to its parent task'''

    tasks = client.tasks.get_tasks_for_project(project_id)
    tasks_list = list(tasks)
    for i in tasks_list:
        if i['name'] == potential_subject:
            parent_gid = i['gid']
    '''loops through all tasks in AMP-SCZ project and assigns the correct subject gid to be linked to the new eeg data'''

    new_eeg_subtask = {
            'name': 'EEG',
            'note': 'EEG data for ' + potential_subject ' has arrived, please do QC!',
            'assignee': 'ojohn@bwh.harvard.edu', #person responsible for doing EEG QC 
            'projects': [project_gid],
            'start_on': eeg_arrival_date,
            'parent': [parent_gid]}

    eeg_subtask = client.tasks.create_in_workspace(ws_gid, new_eeg_subtask)
    '''creates the subtask in asana'''
    eeg_subtask_section = client.sections.add_task_for_section('1202669181415155', {'task': eeg_subtask['gid']})
    '''moves the subtask to Data QC section in AMP-SCZ project'''
    eeg_subtask_dependent = client.tasks.add_dependents_for_task(parent_gid, {'dependents': eeg_subtask['gid']})
    '''links the eeg subtask to its parent task as a dependent'''
    return eeg_subtask

def get_asana_ready() -> tuple:
    token = read_token()
    client = asana.Client.access_token(token)

    workspace_gid = next(client.workspaces.get_workspaces())['gid']
    projects = client.projects.get_projects_for_workspace(workspace_gid)
    for project in projects:
        if project['name'] == 'AMP SCZ':
            project_gid = project['gid']

    return client, workspace_gid, project_gid

if __name__ == '__main__':

    client, workspace_gid, project_gid = get_asana_ready()
    create_new_task('test', workspace_gid, project_gid)

    # amp_scz = client.projects.get_project(project_gid)
    # amp_scz_gid = amp_scz['gid']
    #update_task_list())['gid']
