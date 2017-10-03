
# developed by Gabi Zapodeanu, TSA, GPO, Cisco Systems

# !/usr/bin/env python3

# this module includes common utilized functions to create applications using PI APIs

import requests
import json
import utils

from modules_init import PI_URL, PI_USER, PI_PASSW
from requests.auth import HTTPBasicAuth  # for Basic Auth

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings


PI_AUTH = HTTPBasicAuth(PI_USER, PI_PASSW)


def pi_get_events():

    """
    This a sample PI API.
    """
    events_list_number=[]
    url = PI_URL + '/webacs/api/v1/data/Events'
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    events = requests.get(url, headers=header, verify=False, auth=PI_AUTH)
    events_json = events.json()
    events_list = events_json['queryResponse']['entityId']
    for event in events_list:
        events_list_number.append(event['$'])

    for event in events_list_number:
        url = PI_URL + '/webacs/api/v1/data/Events/' + event
        header = {'content-type': 'application/json', 'accept': 'application/json'}
        event = requests.get(url, headers=header, verify=False, auth=PI_AUTH)
        event_json = event.json()
        utils.pprint(event_json)


def pi_get_client_details():

    """
    This a sample PI API.
    """
    clients_list_number = []
    url = PI_URL + '/webacs/api/v2/data/ClientDetails'
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    clients = requests.get(url, headers=header, verify=False, auth=PI_AUTH)
    clients_json = clients.json()
    clients_list = clients_json['queryResponse']['entityId']

    for client in clients_list:
        clients_list_number.append(client['$'])

    for client in clients_list_number:
        url = PI_URL + '/webacs/api/v2/data/ClientDetails/' + client
        header = {'content-type': 'application/json', 'accept': 'application/json'}
        client = requests.get(url, headers=header, verify=False, auth=PI_AUTH)
        client_json = client.json()
        utils.pprint(client_json)


def pi_get_client_sessions():

    """
    This a sample PI API.
    """
    sessions_list_number = []
    url = PI_URL + '/webacs/api/v1/data/ClientSessions'
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    sessions = requests.get(url, headers=header, verify=False, auth=PI_AUTH)
    sessions_json = sessions.json()
    sessions_list = sessions_json['queryResponse']['entityId']

    for session in sessions_list:
        sessions_list_number.append(session['$'])

    for session in sessions_list_number:
        url = PI_URL + '/webacs/api/v1/data/ClientSessions/' + session
        header = {'content-type': 'application/json', 'accept': 'application/json'}
        session = requests.get(url, headers=header, verify=False, auth=PI_AUTH)
        session_json = session.json()
        utils.pprint(session_json)


def pi_get_device_id(device_name):
    """
    Find out the PI device Id using the device hostname
    Call to Prime Infrastructure - /webacs/api/v1/data/Devices, filtered using the Device Hostname
    :param device_name: device hostname
    :return: PI device Id
    """

    url = PI_URL + '/webacs/api/v1/data/Devices?deviceName=' + device_name
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, verify=False, auth=PI_AUTH)
    device_id_json = response.json()
    device_id = device_id_json['queryResponse']['entityId'][0]['$']
    return device_id


def pi_deploy_cli_template(device_id, template_name, variable_value):
    """
    Deploy a template to a device through Job
    Call to Prime Infrastructure - /webacs/api/v1/op/cliTemplateConfiguration/deployTemplateThroughJob
    :param device_id: PI device id
    :param template_name: the name of the template to be deployed
    :param variable_value: the values of the variables, if needed
    :return: PI job name
    """

    param = {
        'cliTemplateCommand': {
            'targetDevices': {
                'targetDevice': {
                    'targetDeviceID': str(device_id),
                    'variableValues': {
                        'variableValue': variable_value
                    }
                }
            },
            'templateName': template_name
        }
    }
    url = PI_URL + '/webacs/api/v1/op/cliTemplateConfiguration/deployTemplateThroughJob'
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.put(url, data=json.dumps(param), headers=header, verify=False, auth=PI_AUTH)
    job_json = response.json()
    job_name = job_json['mgmtResponse']['cliTemplateCommandJobResult']['jobName']
    return job_name


def pi_get_job_status(job_name):
    """
    Get job status in PI
    Call to Prime Infrastructure - /webacs/api/v1/data/JobSummary, filtered by the job name, will provide the job id
    A second call to /webacs/api/v1/data/JobSummary using the job id
    :param job_name: Prime Infrastructure job name
    :return: PI job status
    """

    #  find out the PI job id using the job name

    url = PI_URL + '/webacs/api/v1/data/JobSummary?jobName=' + job_name
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, verify=False, auth=PI_AUTH)
    job_id_json = response.json()
    job_id = job_id_json['queryResponse']['entityId'][0]['$']

    #  find out the job status using the job id

    url = PI_URL + '/webacs/api/v1/data/JobSummary/' + job_id
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, verify=False, auth=PI_AUTH)
    job_status_json = response.json()
    #  print(json.dumps(job_status_json, indent=4, separators=(' , ', ' : ')))
    job_status = job_status_json['queryResponse']['entity'][0]['jobSummaryDTO']['resultStatus']
    return job_status


def pi_delete_cli_template(cli_template_name):
    """
    This function will delete the PI CLI template with the name {cli_template_name}
    API call to /webacs/api/v1/op/cliTemplateConfiguration/deleteTemplate
    :param cli_template_name: the CLI template to be deleted
    :return: none
    """

    url = PI_URL + '/webacs/api/v1/op/cliTemplateConfiguration/deleteTemplate?templateName='+cli_template_name
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.delete(url, headers=header, verify=False, auth=PI_AUTH)
    if response.status_code == 200:
        print('PI CLI Template with the name: ', cli_template_name, ' deleted')
    else:
        print('PI CLI Template with the name: ', cli_template_name, ' does not exist')


def pi_update_cli_template(vlan_id,remote_client,file):
    """
    This function will update an existing CLI template with the values to be used for deployment
    :param vlan_id: VLAN ID of the remote client
    :param remote_client: IP address for the remote client
    :param file: file that contains the CLI template
    :return: will save the DATETIME+{file} file with the template to be deployed
    """
    file_in = open(file, 'r')
    file_out = open(CLI_DATE_TIME+file, 'w')
    for line in file_in:
        line = line.replace('$VlanId',vlan_id)
        line = line.replace('$RemoteClient',remote_client)
        file_out.write(line)
        print(line)
    file_in.close()
    file_out.close()


def pi_clone_cli_template(file):
    """
    This function will clone an existing CLI template with the name {file}. The new CLI template name will have
    the name DATETIME+{file}
    :param file: file that contains the CLI template
    :return: will save the DATETIME+{file} file with the template to be deployed
    """
    file_in = open(file, 'r')
    file_out = open(CLI_DATE_TIME+' '+file, 'w')
    for line in file_in:
        file_out.write(line)
    file_in.close()
    file_out.close()
    cloned_file_name = CLI_DATE_TIME+' '+file
    return cloned_file_name


def pi_upload_cli_template(cli_file_name, cli_template, list_variables):
    """
    This function will upload a new CLI template from the text file {cli_file_name}.
    It will check if the PI CLI template exists and if yes, it will delete the CLI template
    API call to /webacs/api/v1/op/cliTemplateConfiguration/upload
    :param list_variables: variables to be sent to Prime, required by the template
    :param cli_template: CLI template name
    :param cli_file_name: cli template text file
    :return: the cli_template_id
    """

    # check if the CLI template exists, if it does, delete the existing template

    cli_template_id = pi_get_cli_template(cli_template)
    if cli_template_id is not None:
        pi_delete_cli_template(cli_template)
        print('Will upload the CLI template: ', cli_template)
    time.sleep(2)  # required by PI pacing
    cli_file = open(cli_file_name, 'r')
    cli_config = cli_file.read()
    param = {
        'cliTemplate': {
            'content': cli_config,
            'description': '',
            'deviceType': 'Routers,Switches and Hubs',
            'name': cli_template,
            'path': '',
            'tags': '',
            'variables': list_variables
        },
        'version': ''
    }
    url = PI_URL + '/webacs/api/v1/op/cliTemplateConfiguration/upload'
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    requests.post(url, json.dumps(param), headers=header, verify=False, auth=PI_AUTH)
    cli_file.close()
    cli_template_id = pi_get_cli_template(cli_template)
    return cli_template_id


def pi_get_cli_template(template):
    """
    This function will check if PI has already a CLI template with the name {template}
    :param template: PI CLI template name
    :return: {None} if the template does not exist, {template id} if template exists
    """
    url = PI_URL + '/webacs/api/v1/data/CliTemplate?name='+template
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    templ = requests.get(url, headers=header, verify=False, auth=PI_AUTH)
    templ_json = templ.json()
    templ_count = templ_json['queryResponse']['@count']
    if templ_count == '1':  # if templ_count is "0", template does not exist
        templ_id = templ_json['queryResponse']['entityId'][0]['$']
    else:
        templ_id = None
    return templ_id



