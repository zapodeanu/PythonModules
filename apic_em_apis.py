
# developed by Gabi Zapodeanu, TSA, GSS, Cisco Systems

# !/usr/bin/env python3

# this module include common utilized functions to create applications using APIC-EM APIs

import requests
import json
import utils

from modules_init import EM_URL, EM_USER, EM_PASSW

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings




def get_service_ticket():
    """
    create the authorization ticket required to access APIC-EM
    Call to APIC-EM - /ticket
    :return: ticket
    """

    payload = {'username': EM_USER, 'password': EM_PASSW}
    url = EM_URL + '/ticket'
    header = {'content-type': 'application/json'}
    ticket_response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    if not ticket_response:
        print('No data returned!')
    else:
        ticket_json = ticket_response.json()
        ticket = ticket_json['response']['serviceTicket']
        print('APIC-EM ticket: ', ticket)
        return ticket


ticket = get_service_ticket()


def locate_client(client_ip, ticket):
    """
    Locate a wired client device in the infrastructure by using the client IP address
    Call to APIC-EM - /host
    :param client_ip: Client IP Address
    :param ticket: APIC-EM ticket
    :return: hostname, interface_name, vlan_Id
    """

    interface_name = None
    hostname = None
    vlan_Id = None
    url = EM_URL + '/host'
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    payload = {'hostIp': client_ip}
    host_response = requests.get(url, params=payload, headers=header, verify=False)
    host_json = host_response.json()
    if not host_json['response']:
        print('The IP address ', client_ip, ' is not used by any client devices')
    else:
        host_info = host_json['response'][0]
        interface_name = host_info['connectedInterfaceName']
        device_id = host_info['connectedNetworkDeviceId']
        vlan_Id = host_info['vlanId']
        hostname = get_hostname_id(device_id, ticket)[0]
        print('The IP address ', client_ip, ' is connected to the network device ', hostname, ',  interface ', interface_name)
    return hostname, interface_name, vlan_Id


def get_hostname_id(device_id, ticket):
    """
    Find out the hostname of the network device with the specified device ID
    Call to APIC-EM - network-device/{id}
    :param device_id: APIC-EM device Id
    :param ticket: APIC-EM ticket
    :return: hostname and the device type of the network device
    """

    url = EM_URL + '/network-device/' + device_id
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    hostname_response = requests.get(url, headers=header, verify=False)
    hostname_json = hostname_response.json()
    hostname = hostname_json['response']['hostname']
    devicetype = hostname_json['response']['type']
    return hostname, devicetype


def get_device_id(device_name, ticket):
    """
    This function will find the APIC-EM device id for the device with the name {device_name}
    :param device_name: device hostname
    :param ticket: APIC-EM ticket
    :return: APIC-EM device id
    """

    url = EM_URL + '/network-device/'
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    device_response = requests.get(url, headers=header, verify=False)
    device_json = device_response.json()
    device_list = device_json['response']
    for device in device_list:
        if device['hostname'] == device_name:
            device_id = device['id']
    return device_id


def sync_device(device_name, ticket):
    """
    This function will sync the device configuration from the device with the name {device_name}
    :param device_name: device hostname
    :param ticket: APIC-EM ticket
    :return: the response, 202 if sync initiated
    """

    device_id = get_device_id(device_name, ticket)
    param = [device_id]
    url = EM_URL + '/network-device/sync'
    header = {'accept': 'application/json', 'content-type': 'application/json', 'X-Auth-Token': ticket}
    sync_response = requests.put(url, data=json.dumps(param), headers=header, verify=False)
    return sync_response.status_code


def create_path_visualisation(src_ip, dest_ip, ticket):
    """
    This function will create a new Path Visualisation between the source IP address {src_ip} and the
    destination IP address {dest_ip}
    :param src_ip: Source IP address
    :param dest_ip: Destination IP address
    :param ticket: APIC-EM ticket
    :return: APIC-EM path visualisation id
    """

    param = {
        'destIP': dest_ip,
        'periodicRefresh': False,
        'sourceIP': src_ip
    }

    url = EM_URL + '/flow-analysis'
    header = {'accept': 'application/json', 'content-type': 'application/json', 'X-Auth-Token': ticket}
    path_response = requests.post(url, data=json.dumps(param), headers=header, verify=False)
    path_json = path_response.json()
    path_id = path_json['response']['flowAnalysisId']
    return path_id


def get_path_visualisation_info(path_id, ticket):
    """
    This function will return the path visualisation details for the APIC-EM path visualisation {id}
    :param path_id: APIC-EM path visualisation id
    :param ticket: APIC-EM ticket
    :return: Path visualisation details in a list [device,interface_out,interface_in,device...]
    """

    url = EM_URL + '/flow-analysis/' + path_id
    header = {'accept': 'application/json', 'content-type': 'application/json', 'X-Auth-Token': ticket}
    path_response = requests.get(url, headers=header, verify=False)
    path_json = path_response.json()
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

