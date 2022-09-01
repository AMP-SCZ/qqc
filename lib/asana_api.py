import asana 

client = asana.Client.access_token('1/1202709400692234:9c229828742b80e4a8ba5c76d8222b8a')

amp_scz = client.projects.get_project('1202669181415152')

amp_scz_gid = amp_scz['gid']


def create_new_task(potential_subject: str):
	#Creates new task to send to AMP SCZ project in Asana
	new_task = {'name': potential_subject, 
		'note': 'New Data has been uploaded for ' + potential_subject,
		'assignee': 'kevincho@bwh.harvard.edu',
		'projects': [amp_scz_gid]}

	created_task = client.tasks.create_in_workspace('958915379528887', new_task)
	
	return created_task


def update_task_list(): 
	tasks = client.tasks.get_tasks_for_project(amp_scz_gid)
	tasks_list = list(tasks)
	print('Returning updated list of all tasks in AMP SCZ project')
	return tasks_list



#update_task_list()


'''def create_new_subtask():
	new_subtask = {'name': 'MRI',
	'note': 'MRI data for subject_id has arrived, please do QC!',
	'assignee': 'ojohn@bwh.harvard.edu', #person responsible for doing MRI QC 
	'projects': [amp_scz_gid],
	'dependents': [update_task_list()[0]['gid']]}'''

