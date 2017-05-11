
# developed by Gabi Zapodeanu, TSA, GSS, Cisco Systems

# !/usr/bin/env python3

# this module includes common utilized functions to create applications using Meraki APIs

import requests
import json
import utils

from modules_init import MERAKI_API_KEY, MERAKI_URL

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings


def get_organizations():
    """
    This function will get the Meraki Organization Id for the user with the MERAKI_API_KEY
    API call to /organizations
    :return: Meraki Organization Ids as a an array of {'name':'id',...}
    """

    url = MERAKI_URL + '/organizations'
    header = {'content-type': 'application/json', 'X-Cisco-Meraki-API-Key': MERAKI_API_KEY}
    org_response = requests.get(url, headers=header, verify=False)
    org_json = org_response.json()
    org_dict = {}
    for org in org_json:
        org_dict.update({org['name']: org['id']})
    return org_dict


def get_organization_id(org_name):
    """
    This function will return the Meraki Organization Id for the Meraki Organization named {org_name}
    :param org_name: Meraki organization name
    :return: Meraki organization id
    """

    org_dict = get_organizations()
    org_id = org_dict[org_name]
    return org_id


def get_networks(org_name):
    """
    This function will return the list of networks associated with the Meraki Organization ID
    API call to /organizations/{organization_id]/networks
    :param org_name: Meraki organization name
    :return: Meraki Network Ids as an array of {'name':'id',...}
    """

    org_id = get_organization_id(org_name)
    url = MERAKI_URL + '/organizations/' + str(org_id) + '/networks'
    header = {'content-type': 'application/json', 'X-Cisco-Meraki-API-Key': MERAKI_API_KEY}
    networks_response = requests.get(url, headers=header, verify=False)
    networks_json = networks_response.json()
    networks_dict = {}
    for netw in networks_json:
        network_id = netw['id']
        network_name = netw['name']
        networks_dict.update({network_name: network_id})
    return networks_dict


def get_network_id(org_name, netw_name):
    """
    This function will return the Meraki Organization Id for the Meraki Organization named {org_name}
    :param org_name: Meraki organization name
    :param netw_name: Meraki network name
    :return: Meraki network id
    """

    netw_dict = get_networks(org_name)
    netw_id = netw_dict[netw_name]
    return netw_id


def get_sm_devices(network_id):
    """
    This function will return the list of networks associated with the Meraki Network ID
    API call to /networks/{organization_id]/sm/devices
    :param network_id: Meraki network ID
    :return: list with all the SM devices
    """

    url = MERAKI_URL + '/networks/' + str(network_id) + '/sm/devices?fields=phoneNumber,location'
    header = {'content-type': 'application/json', 'X-Cisco-Meraki-API-Key': MERAKI_API_KEY}
    sm_devices_response = requests.get(url, headers=header, verify=False)
    sm_devices_json = sm_devices_response.json()['devices']
    return sm_devices_json


def get_devices(network_id):
    """
    This function will return a list with all the network devices associated with the Meraki Network Id
    :param network_id: Meraki Network ID
    :return: list with all the devices
    """
    url = MERAKI_URL + '/networks/' + str(network_id) + '/devices'
    header = {'content-type': 'application/json', 'X-Cisco-Meraki-API-Key': MERAKI_API_KEY}
    devices_response = requests.get(url, headers=header, verify=False)
    devices_json = devices_response.json()
    return devices_json


def get_user_cell(users_info, email):
    """
    This function will look up the user cell phone based on his email
    :param users_info: List of all the users info
    :param user_email: user email address
    :return: the user cell phone number
    """

    user_cell = None
    for user in users_info:
        if user['email'] == email:
            user_cell = user['cell']
    return user_cell


def get_location_cell(sm_devices_list, user_cell):
    """
    This function will locate the user based on his cell phone number
    :param sm_devices_list: the list of Meraki SM devices
    :param user_cell: user cell phone number
    :return: the user location
    """
    location = None
    for device in sm_devices_list:
        if device['phoneNumber'] == user_cell:
            pprint(device)
            location = device['location']
    return location


def get_ssids(network_id):
    """
    This function will return the Meraki Network id list of configured SSIDs
    :param network_id: Meraki Network id
    :return: list of SSIDs
    """
    url = MERAKI_URL + '/networks/' + str(network_id) + '/ssids'
    header = {'content-type': 'application/json', 'X-Cisco-Meraki-API-Key': MERAKI_API_KEY}
    ssids_response = requests.get(url, headers=header, verify=False)
    ssids_json = ssids_response.json()

    # filter only configured SSIDs
    ssids_list = []
    for ssid in ssids_json:
        if 'Unconfigured' not in ssid['name']:
            ssids_list.append(ssid)
    return ssids_list


def meraki_enable_ssid(network_id,ssid_number):
    """
    This function will enable the SSID with the {ssid_number}, from the Meraki network with the network_id
    :param network_id: Meraki network id
    :param ssid_number: Meraki SSID number
    :return:
    """
    url = MERAKI_URL + '/networks/' + str(network_id) + '/ssids/' + str(ssid_number)
    payload = {'enabled': True}
    header = {'content-type': 'application/json', 'X-Cisco-Meraki-API-Key': MERAKI_API_KEY}
    enable_ssid_response = requests.put(url, data=json.dumps(payload), headers=header, verify=False)
    enable_ssid_json = enable_ssid_response.json()
    return enable_ssid_json


def main():
    organizations = get_organizations()
    utils.pprint(organizations)
    print(get_organization_id('Meraki Live Demo'))
    print(get_networks('Meraki Live Demo'))
    utils.pprint(get_networks('Meraki Live Demo'))
    print(get_network_id('Meraki Live Demo','San Francisco'))


if __name__ == '__main__':
    main()
