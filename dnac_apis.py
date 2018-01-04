
# developed by Gabi Zapodeanu, TSA, GPO, Cisco Systems

# !/usr/bin/env python3

import requests
import json

import requests.packages.urllib3

from requests.packages.urllib3.exceptions import InsecureRequestWarning

from requests.auth import HTTPBasicAuth  # for Basic Auth

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings

# use the DNA Center controller

DNAC_URL = 'https://172.28.97.216'
DNAC_USER = 'admin'
DNAC_PASS = 'Cisco123'

DNAC_URL = 'https://10.93.140.80'
DNAC_USER = 'admin'
DNAC_PASS = 'C1sco1234'

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
    template_id = None
    template_list = get_template_info(dnac_token)
    for template in template_list:
        if template['name'] == template_name:
            template_id = template['versionsInfo'][-1]['id']  # to get the last template version
    return template_id


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

    :param devive_name:
    :param dnac_jwt_token:
    :return:
    """
    device_info = get_all_device_info(dnac_jwt_token)
    device_list = device_info['response']
    for device in device_list:
        if device['hostname'] == device_name:
            device_id = device['id']
    return device_id


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


def deploy_template(template_name, device_name, dnac_jwt_token):
    """

    :param template_name:
    :param device_name:
    :param dnac_jwt_token:
    :return:
    """
    device_id = get_device_id_name(device_name, dnac_jwt_token)
    print(device_id)
    template_id = get_template_id(template_name, dnac_jwt_token)
    print(template_id)
    payload = {
            "name": "DCRConfig",
            "templateParams": [
                {
                "deviceId": "93c4b80d-baf2-4d6c-93c7-786d162e6d9b"
                }
            ]
        }
    pprint(payload)
    url = DNAC_URL + '/api/v1/template-programmer/template/deploy'
    print(url)
    header = {'content-type': 'application/json', 'Cookie': dnac_jwt_token}
    response = requests.post(url, headers=header, data=json.dumps(payload), verify=False)
    print(response)
    print(response.status_code)


def create_area(area_name, ticket):
    """
    The function will create a new area with the name {area_name}
    :param area_name: DNA C area name
    :param ticket: DNA C ticket
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
        "groupNameHierarchy": "Global/USA/" + area_name,
        "groupTypeList": [
            "SITE"
        ],
        "systemGroup": False,
        "parentId": "",
        "name": area_name,
        "id": ""
    }
    url = DNAC_URL + '/group'
    header = {'content-type': 'application/json', 'X-Auth-Token': ticket}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)


def create_site(site_name, area_name, address, ticket):
    """
    The function will create a new site with the name {site_name}, part of the area with the name {area_name}
    :param site_name: DNA C site name
    :param area_name: DNA C area name
    :param address: site address
    :param ticket: DNA C ticket
    :return: none
    """
    # get the area id for the area name

    area_id = get_area_id(area_name, ticket)

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
        "groupNameHierarchy": "Global/USA/" + site_name,
        "groupTypeList": [
            "SITE"
        ],
        "systemGroup": False,
        "parentId": area_id,
        "name": site_name,
        "id": ""
    }
    url = DNAC_URL + '/group'
    header = {'content-type': 'application/json', 'X-Auth-Token': ticket}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)


def create_floor(site_name, floor_name, floor_number, ticket):
    """
    The function will  create a floor in the building with the name {site_name}
    :param site_name: DNA C site name
    :param floor_name: floor name
    :param floor_number: floor number
    :param ticket: DNA C ticket
    :return: none
    """
    # get the site id
    site_id = get_site_id(site_name, ticket)

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
                    "width": "300.0",
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
        "groupNameHierarchy": "Global/USA/Lake Oswego/" + floor_name,
        "groupTypeList": [
            "SITE"
        ],
        "name": floor_name,
        "parentId": site_id,
        "systemGroup": False,
        "id": ""
    }
    url = DNAC_URL + '/group'
    header = {'content-type': 'application/json', 'X-Auth-Token': ticket}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)





def assign_device_site(device_sn, site_name, ticket):
    """
    This function will assign a device with the specified SN to a site with the name {site_name}
    :param device_sn: network device SN
    :param site_name: DNA C site name
    :param ticket: DNA C ticket
    :return:
    """
    site_id = get_site_id(site_name, ticket)
    device_id = get_device_id(device_sn, ticket)
    url = DNAC_URL + '/group/' + site_id + '/member'
    payload = {"networkdevice": [device_id]}
    header = {'content-type': 'application/json', 'X-Auth-Token': ticket}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    print('\nDevice with the SN: ', device_sn, 'assigned to site: ', site_name)


def get_area_id(area_name, ticket):
    """
    The function will return the DNA C area id for the area with the name {area_name}
    :param area_name: DNA C area name
    :param ticket: DNA C ticket
    :return: DNA C area id
    """
    url = DNAC_URL + '/group?groupType=SITE'
    header = {'content-type': 'application/json', 'X-Auth-Token': ticket}
    area_response = requests.get(url, headers=header, verify=False)
    area_json = area_response.json()
    area_list = area_json['response']
    for area in area_list:
        if area_name == area['name']:
            area_id = area['id']
    return area_id


def get_site_id(site_name, ticket):
    """
    The function will get the DNA C site id for the site with the name {site_name}
    :param site_name: DNA C site name
    :param ticket: DNA C ticket
    :return: DNA C site id
    """
    url = DNAC_URL + '/group?groupType=SITE'
    header = {'content-type': 'application/json', 'X-Auth-Token': ticket}
    site_response = requests.get(url, headers=header, verify=False)
    site_json = site_response.json()
    site_list = site_json['response']
    for site in site_list:
        if site_name == site['name']:
            site_id = site['id']
    return site_id


dnac_token = get_dnac_jwt_token(DNAC_AUTH)
print(dnac_token)

print('templ-id', get_template_id('DCRConfig', dnac_token))
print('device-id', get_device_id_name('NYC-9300', dnac_token))
print('device id sn', get_device_id_sn('FOC1802X0SC', dnac_token))
deploy_template('DCRConfig', 'NYC-9300', dnac_token)

