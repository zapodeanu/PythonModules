
# developed by Gabi Zapodeanu, TSA, GPO, Cisco Systems

# !/usr/bin/env python3

import requests
import json
import time

import requests.packages.urllib3

from requests.packages.urllib3.exceptions import InsecureRequestWarning

from requests.auth import HTTPBasicAuth  # for Basic Auth

# from modules_init import GOOGLE_API_KEY

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings

# use the DNA Center controller

DNAC_URL = 'https://172.28.97.216'
DNAC_USER = 'admin'
DNAC_PASS = 'Cisco123'

# DNAC_URL = 'https://10.93.140.80'
# DNAC_USER = 'admin'
# DNAC_PASS = 'C1sco1234'

DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data: data to pretty print
    :return:
    """
    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def get_dnac_jwt_token(dnac_auth):
    """
    Create the authorization token required to access DNA C
    Call to DNA C - /api/system/v1/auth/login
    :param dnac_auth - DNA C Basic Auth string
    :return: DNA C JWT token
    """

    url = DNAC_URL + '/api/system/v1/auth/login'
    header = {'content-type': 'application/json'}
    response = requests.get(url, auth=dnac_auth, headers=header, verify=False)
    response_header = response.headers
    dnac_jwt_token = response_header['Set-Cookie']
    return dnac_jwt_token


def get_all_device_info(dnac_jwt_token):
    """
    The function will return all network devices info
    :param dnac_jwt_token: DNA C token
    :return: DNA C device inventory info
    """
    url = DNAC_URL + '/api/v1/network-device'
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    all_device_response = requests.get(url, headers=header, verify=False)
    all_device_info = all_device_response.json()
    return all_device_info


def get_template_info(dnac_jwt_token):
    """
    This function will return the info for all CLI templates existing on DNA C
    :param dnac_jwt_token: DNA C token
    :return: all info for all templates
    """
    url = DNAC_URL + '/api/v1/template-programmer/template'
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    response = requests.get(url, headers=header, verify=False)
    template_json = response.json()
    return template_json


def get_template_id(template_name, dnac_jwt_token):
    """
    This function will return the template id for the DNA C template with the name {template_name}
    :param template_name: name of the template
    :param dnac_jwt_token: DNA C token
    :return: DNA C template id
    """
    template_list = get_template_info(dnac_token)
    template_id = 'template'
    for template in template_list:
        if template['name'] == template_name:
            template_version_list = template['versionsInfo']
            pprint(template_version_list)
            # to get the last template version, the template list is not ordered
            version_list_len = len(template_version_list)
            for version in template_version_list:
                if version['version'] == str(version_list_len):
                    template_id = version['id']
    return template_id


def deploy_template(template_name, device_name, dnac_jwt_token):
    """
    This function will deploy the template with the name {template_name} to the network device with the name
    {device_name}
    :param template_name: template name
    :param device_name: device hostname
    :param dnac_jwt_token: DNA C token
    :return: deployment status ({202} if successful), and the deployment task id
    """
    device_management_ip = get_device_management_ip_name(device_name, dnac_jwt_token)
    template_id = get_template_id(template_name, dnac_jwt_token)
    print(template_id)
    payload = {
            "templateId": template_id,
            "targetInfo": [
                {
                    "id": device_management_ip,
                    "type": "MANAGED_DEVICE_IP",
                    "params": {}
                }
            ]
        }
    pprint(payload)
    url = DNAC_URL + '/api/v1/template-programmer/template/deploy'
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    response = requests.post(url, headers=header, data=json.dumps(payload), verify=False)
    print(response.text)
    depl_status = response.status_code
    depl_task_id = (response.json())["deploymentId"]
    return depl_status, depl_task_id


def check_template_deployment_status(depl_task_id, dnac_jwt_token):
    """
    This function will check the result for the deployment of the CLI template with the id {depl_task_id}
    :param depl_task_id: template deployment id
    :param dnac_jwt_token: DNA C token
    :return: status - {SUCCESS} = successful, {FAILURE} = unsuccessful
    """
    url = DNAC_URL + '/api/v1/template-programmer/template/deploy/status/' + deployment_task_id
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    response = requests.get(url, headers=header, verify=False)
    response_json = response.json()
    pprint(response_json)
    deployment_status = response_json["status"]
    return deployment_status


def locate_client_ip(client_ip, dnac_jwt_token):
    """
    Locate a wired client device in the infrastructure by using the client IP address
    Call to DNA C - api/v1/host?hostIp={client_ip}
    :param client_ip: Client IP Address
    :param ticket: APIC-EM ticket
    :return: hostname, interface_name, vlan_id
    """
    url = DNAC_URL + '/api/v1/host?hostIp=' + client_ip
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    response = requests.get(url, headers=header, verify=False)
    client_info = response.json()
    hostname = client_info['response'][0]['connectedNetworkDeviceName']
    interface_name = client_info['response'][0]['connectedInterfaceName']
    vlan_id = client_info['response'][0]['vlanId']
    return hostname, interface_name, vlan_id


def get_device_id_name(device_name, dnac_jwt_token):
    """
    This function will find the DNA C device id for the device with the name {device_name}
    :param device_name: device hostname
    :param dnac_jwt_token: DNA C token
    :return:
    """
    device_info = get_all_device_info(dnac_jwt_token)
    device_list = device_info['response']
    for device in device_list:
        if device['hostname'] == device_name:
            device_id = device['id']
    return device_id


def get_device_management_ip_name(device_name, dnac_jwt_token):
    """
    This function will find out the management IP address for the device with the name {device_name}
    :param device_name: device name
    :param dnac_jwt_token: DNA C token
    :return: the management ip address
    """
    device_info = get_all_device_info(dnac_jwt_token)
    device_list = device_info['response']
    for device in device_list:
        if device['hostname'] == device_name:
            device_ip = device['managementIpAddress']
    return device_ip


def get_device_id_sn(device_sn, dnac_jwt_token):
    """
    The function will return the DNA C device id for the device with serial number {device_sn}
    :param device_sn: network device SN
    :param dnac_jwt_token: DNA C token
    :return: DNA C device id
    """
    url = DNAC_URL + '/api/v1/network-device/serial-number/' + device_sn
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    device_response = requests.get(url, headers=header, verify=False)
    device_info = device_response.json()
    device_id = device_info['response']['id']
    return device_id


def create_site(site_name, dnac_jwt_token):
    """
    The function will create a new site with the name {site_name}
    :param site_name: DNA C site name
    :param dnac_jwt_token: DNA C token
    :return: none
    """
    payload = {
        "additionalInfo": [
            {
                "nameSpace": "Location",
                "attributes": {
                    "type": "area"
                }
            }
        ],
        "groupNameHierarchy": "Global/" + site_name,
        "groupTypeList": [
            "SITE"
        ],
        "systemGroup": False,
        "parentId": "",
        "name": site_name,
        "id": ""
    }
    url = DNAC_URL + '/api/v1/group'
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)


def get_site_id(site_name, dnac_jwt_token):
    """
    The function will get the DNA C site id for the site with the name {site_name}
    :param site_name: DNA C site name
    :param dnac_jwt_token: DNA C token
    :return: DNA C site id
    """
    url = DNAC_URL + '/api/v1/group?groupType=SITE'
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    site_response = requests.get(url, headers=header, verify=False)
    site_json = site_response.json()
    site_list = site_json['response']
    for site in site_list:
        if site_name == site['name']:
            site_id = site['id']
    return site_id


def create_building(site_name, building_name, address, dnac_jwt_token):
    """
    The function will create a new building with the name {building_name}, part of the site with the name {site_name}
    :param site_name: DNA C site name
    :param building_name: DNA C building name
    :param address: building address
    :param dnac_jwt_token: DNA C token
    :return: none
    """
    # get the site id for the site name
    site_id = get_site_id(site_name, dnac_jwt_token)

    # get the geolocation info for address
    geo_info = get_geo_info(address, GOOGLE_API_KEY)
    print('\nGeolocation info for the address ', address, ' is:')
    pprint(geo_info)

    payload = {
        "additionalInfo": [
            {
                "nameSpace": "Location",
                "attributes": {
                    "country": "United States",
                    "address": address,
                    "latitude": geo_info['lat'],
                    "type": "building",
                    "longitude": geo_info['lng']
                }
            }
        ],
        "groupNameHierarchy": "Global/" + site_name + '/' + building_name,
        "groupTypeList": [
            "SITE"
        ],
        "systemGroup": False,
        "parentId": site_id,
        "name": building_name,
        "id": ""
    }
    url = DNAC_URL + '/api/v1/group'
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)


def get_building_id(building_name, dnac_jwt_token):
    """
    The function will get the DNA C building id for the building with the name {building_name}
    :param building_name: building name
    :param dnac_jwt_token: DNA C token
    :return: DNA C building id
    """
    url = DNAC_URL + '/api/v1/group?groupType=SITE'
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    building_response = requests.get(url, headers=header, verify=False)
    building_json = building_response.json()
    building_list = building_json['response']
    for building in building_list:
        if building_name == building['name']:
            building_id = building['id']
    return building_id


def create_floor(building_name, floor_name, floor_number, dnac_jwt_token):
    """
    The function will  create a floor in the building with the name {site_name}
    :param building_name: DNA C site name
    :param floor_name: floor name
    :param floor_number: floor number
    :param dnac_jwt_token: DNA C token
    :return: none
    """
    # get the site id
    building_id = get_building_id(building_name, dnac_jwt_token)

    payload = {
        "additionalInfo": [
            {
                "nameSpace": "Location",
                "attributes": {
                    "type": "floor"
                }
            },
            {
                "nameSpace": "mapGeometry",
                "attributes": {
                    "offsetX": "0.0",
                    "offsetY": "0.0",
                    "width": "200.0",
                    "length": "100.0",
                    "geometryType": "DUMMYTYPE",
                    "height": "20.0"
                }
            },
            {
                "nameSpace": "mapsSummary",
                "attributes": {
                    "floorIndex": floor_number
                }
            }
        ],
        "groupNameHierarchy": "",
        "groupTypeList": [
            "SITE"
        ],
        "name": floor_name,
        "parentId": building_id,
        "systemGroup": False,
        "id": ""
    }
    url = DNAC_URL + '/api/v1/group'
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)


def get_floor_id(building_name, floor_name, dnac_jwt_token):
    """
    This function will return the floor id for the floor with the name {floor_name} located in the building with the
    name {building_name}
    :param building_name: building name
    :param floor_name: floor name
    :param dnac_jwt_token: DNA C token
    :return: floor_id
    """
    building_id = get_building_id(building_name, dnac_jwt_token)
    url = DNAC_URL + '/api/v1/group' + building_id + '/child?level=1'
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    building_response = requests.get(url, headers=header, verify=False)
    building_json = building_response.json()
    floor_list = building_json['response']
    for floor in floor_list:
        if floor['name'] == floor_name:
            floor_id = floor['id']
    return floor_id


def assign_device_sn_building(device_sn, building_name, dnac_jwt_token):
    """
    This function will assign a device with the specified SN to a building with the name {building_name}
    :param device_sn: network device SN
    :param building_name: DNA C building name
    :param dnac_jwt_token: DNA C token
    :return:
    """
    # get the building and device id's
    building_id = get_building_id(building_name, dnac_jwt_token)
    device_id = get_device_id_sn(device_sn, dnac_jwt_token)

    url = DNAC_URL + '/api/v1/group/' + building_id + '/member'
    payload = {"networkdevice": [device_id]}
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    print('\nDevice with the SN: ', device_sn, 'assigned to building: ', building_name)


def assign_device_name_building(device_name, building_name, dnac_jwt_token):
    """
    This function will assign a device with the specified name to a building with the name {building_name}
    :param device_name: network device name
    :param building_name: DNA C building name
    :param dnac_jwt_token: DNA C token
    :return:
    """
    # get the building and device id's
    building_id = get_building_id(building_name, dnac_jwt_token)
    device_id = get_device_id_name(device_name, dnac_jwt_token)

    url = DNAC_URL + '/api/v1/group/' + building_id + '/member'
    payload = {"networkdevice": [device_id]}
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    print('\nDevice with the name: ', device_name, 'assigned to building: ', building_name)


def get_geo_info(address, google_key):
    """
    The function will access Google Geolocation API to find the longitude/latitude for a address
    :param address: address, including ZIP and Country
    :param google_key: Google API Key
    :return: longitude/latitude
    """
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=' + google_key
    header = {'content-type': 'application/json'}
    response = requests.get(url, headers=header, verify=False)
    response_json = response.json()
    location_info = response_json['results'][0]['geometry']['location']
    return location_info


def sync_device(device_name, dnac_jwt_token):
    """
    This function will sync the device configuration from the device with the name {device_name}
    :param device_name: device hostname
    :param dnac_jwt_token: DNA C token
    :return: the response status code, 202 if sync initiated, and the task id
    """
    device_id = get_device_id_name(device_name, dnac_jwt_token)
    param = [device_id]
    url = DNAC_URL + '/api/v1/network-device/sync?forceSync=true'
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    sync_response = requests.put(url, data=json.dumps(param), headers=header, verify=False)
    task = sync_response.json()['response']['taskId']
    return sync_response.status_code, task


def check_task_id_status(task_id, dnac_jwt_token):
    """
    This function will check the status of the task with the id {task_id}
    :param task_id: task id
    :param dnac_jwt_token: DNA C token
    :return: status - {SUCCESS} = successful, {FAILURE} = unsuccessful
    """
    url = DNAC_URL + '/api/v1/task/' + task_id
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    task_response = requests.get(url, headers=header, verify=False)
    task_json = task_response.json()
    task_status = task_json['response']['isError']
    if task_status == False:
        task_result = 'SUCCESS'
    else:
        task_result = 'FAILURE'
    return task_result


def create_path_visualisation(src_ip, dest_ip, dnac_jwt_token):
    """
    This function will create a new Path Visualisation between the source IP address {src_ip} and the
    destination IP address {dest_ip}
    :param src_ip: Source IP address
    :param dest_ip: Destination IP address
    :param dnac_jwt_token: DNA C token
    :return: DNA C path visualisation id
    """

    param = {
        'destIP': dest_ip,
        'periodicRefresh': False,
        'sourceIP': src_ip
    }

    url = DNAC_URL + '/api/v1/flow-analysis'
    header = {'accept': 'application/json', 'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    path_response = requests.post(url, data=json.dumps(param), headers=header, verify=False)
    path_json = path_response.json()
    print(path_response.status_code)
    print(path_response.text)
    path_id = path_json['response']['flowAnalysisId']
    return path_id


def get_path_visualisation_info(path_id, dnac_jwt_token):
    """
    This function will return the path visualisation details for the APIC-EM path visualisation {id}
    :param path_id: DNA C path visualisation id
    :param dnac_jwt_token: DNA C token
    :return: Path visualisation details in a list [device,interface_out,interface_in,device...]
    """

    url = DNAC_URL + '/api/v1/flow-analysis/' + path_id
    header = {'accept': 'application/json', 'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    path_response = requests.get(url, headers=header, verify=False)
    path_json = path_response.json()
    print(path_response.status_code)
    pprint(path_json)
    path_info = path_json['response']
    path_status = path_info['request']['status']
    path_list = []
    if path_status == 'COMPLETED':
        network_info = path_info['networkElementsInfo']
        path_list.append(path_info['request']['sourceIP'])
        for elem in network_info:
            try:
                path_list.append(elem['ingressInterface']['physicalInterface']['name'])
            except:
                pass
            try:
                path_list.append(elem['name'])
            except:
                pass
            try:
                path_list.append(elem['egressInterface']['physicalInterface']['name'])
            except:
                pass
        path_list.append(path_info['request']['destIP'])
    return path_status, path_list



dnac_token = get_dnac_jwt_token(DNAC_AUTH)
print('DNA C Token: ', dnac_token)

deployment = deploy_template('GRERemoteConfig', 'NYC-9300', dnac_token) # to test template deployments

deployment_task_id = deployment[1]

time.sleep(5)

# check_template_deployment_status(deployment_task_id, dnac_token))

# create_site('USA', dnac_token)
# print('site id', get_site_id('USA', dnac_token))
# create_building('USA', 'Sherwood', '23742 SW Pinehurst Dr., Sherwood, OR 97140', dnac_token)
# print(get_building_id('Sherwood',dnac_token))

# create_floor('Sherwood', 'Floor 1', '1', dnac_token)
# print(get_floor_id('Sherwood', 'Floor 1', dnac_token  ))

# assign_device_sn_building('FCW2123L0N3', 'Manhattan', dnac_token)
# assign_device_name_building('PDX-RO', 'Lake Oswego', dnac_token)

# sync_return = []
# sync_return = sync_device('PDX-RO', dnac_token)
# task_id = sync_return[1]
# print('task id ', task_id)
# print('status code ', sync_return[0])

# time.sleep(3)

# print(check_task_id_status(task_id, dnac_token))

# path_trace_id = (create_path_visualisation('10.93.130.21', '10.93.140.35', dnac_token))
# print(path_trace_id)
# time.sleep(30)

# get_path_visualisation_info(path_trace_id, dnac_token)