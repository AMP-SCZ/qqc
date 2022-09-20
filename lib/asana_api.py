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
                    proj_gid: str) -> 'asana.task':
    '''Creates new task to send to AMP SCZ project in Asana

    Note:
        subject_info_dict = {'consent_date': 'YYYY-MM-DD'}

    '''
    new_task = {
        'name': potential_subject,
        'note': 'New Data has been uploaded for ' + potential_subject,
        'assignee': 'kevincho@bwh.harvard.edu',
        'projects': [proj_gid]}

    created_task = client.tasks.create_in_workspace(ws_gid, new_task)'consent_date': 'YYYY-MM-DD'}

    return created_task


def update_task_list(proj_gid):
    tasks = client.tasks.get_tasks_for_project(proj_gid)
    tasks_list = list(tasks)
    print('Returning updated list of all tasks in AMP SCZ project')
    return tasks_list


'''def create_new_subtask():
    new_subtask = {'name': 'MRI',
    'note': 'MRI data for subject_id has arrived, please do QC!',
    'assignee': 'ojohn@bwh.harvard.edu', #person responsible for doing MRI QC 
    'projects': [amp_scz_gid],
    'dependents': [update_task_list()[0]['gid']]}'''
'''hahah'''

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
