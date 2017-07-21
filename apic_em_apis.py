
# developed by Gabi Zapodeanu, TSA, GPO, Cisco Systems


# !/usr/bin/env python3


# this module includes common utilized functions to create applications using APIC-EM APIs


import requests
import json
import utils

from modules_init import EM_URL

from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings


def get_service_ticket(username, password):
    """
    Create the authorization ticket required to access APIC-EM
    Call to APIC-EM - /ticket
    :param username: the username
    :param password: the password
    :return: ticket
    """

    payload = {'username': username, 'password': password}
    url = EM_URL + '/ticket'
    header = {'content-type': 'application/json'}
    ticket_response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    if not ticket_response:
        print('No data returned!')
    else:
        ticket_json = ticket_response.json()
        ticket = ticket_json['response']['serviceTicket']
        return ticket


def find_client(client_ip, ticket):
    """
    Locate a wired client device in the infrastructure by using the client IP address
    Call to APIC-EM - /host
    :param client_ip: Client IP Address
    :param ticket: APIC-EM ticket
    :return: hostname, interface_name, vlan_Id
    """

    interface_name = None
    hostname = None
    vlan_id = None
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
        vlan_id = host_info['vlanId']
        hostname = get_hostname_id(device_id, ticket)[0]
        print('The IP address ', client_ip, ' is connected to the network device ', hostname, ',  interface ', interface_name)
    return hostname, interface_name, vlan_id


def get_hostname_id(device_id, ticket):
    """
    Find out the hostname of the network device with the specified device ID
    Call to APIC-EM - network-device/{id}
    :param device_id: APIC-EM device Id
    :param ticket: APIC-EM ticket
    :return: hostname and the device type of the network device
    """

    url = EM_URL + '/network-device/' + device_id
    header = {'accept': 'application/xml', 'X-Auth-Token': ticket}
    hostname_response = requests.get(url, headers=header, verify=False)
    hostname_json = hostname_response.json()
    hostname = hostname_json['response']['hostname']
    devicetype = hostname_json['response']['type']
    return hostname, devicetype


def get_hostname_ip(device_ip, ticket):
    """
    The function will find out the hostname of the network device with the specified management IP address
    API call to /network-device/ip-address/{ip-address}
    :param device_ip: IP address to check
    :param ticket: APIC-EM ticket
    :return: network device hostname and type
    """

    url = EM_URL + '/network-device/ip-address/' + device_ip
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    hostname_response = requests.get(url, headers=header, verify=False)
    hostname_json = hostname_response.json()
    hostname = hostname_json['response']['hostname']
    device_type = hostname_json['response']['type']
    return hostname, device_type


def get_device_id(device_name, ticket):
    """
    This function will find the APIC-EM device id for the device with the name {device_name}
    API call to /network-device
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


def check_client_ip_address(client_ip, ticket):
    """
    The function will find out if APIC-EM has a client device configured with the specified IP address.
    API call to /host
    It will print if a client device exists or not.
    :param client_ip: client IP address
    :param ticket: APIC-EM ticket
    :return: None
    """

    url = EM_URL + '/host'
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    payload = {'hostIp': client_ip}
    host_response = requests.get(url, params=payload, headers=header, verify=False)
    host_json = host_response.json()
    if not host_json['response']:
        print('The IP address', client_ip, 'is not used by any client devices')
    else:
        print('The IP address', client_ip, 'is used by a client device')
        host_info = host_json['response'][0]
        host_type = host_info['hostType']
        host_vlan = host_info['vlanId']

        # verification required for wireless clients, JSON output is different for wireless vs. wired clients

        if host_type == 'wireless':

            # info for wireless clients

            apic_em_device_id = host_info['connectedNetworkDeviceId']
            hostname = get_hostname_id(apic_em_device_id, ticket)[0]
            device_type = get_hostname_id(apic_em_device_id, ticket)[1]
            print('\nThe IP address', client_ip, ', is connected to the network device:', hostname,
                  ', model:', device_type, ', interface VLAN:', host_vlan)
            interface_name = host_vlan
        else:

            # info for ethernet connected clients

            interface_name = host_info['connectedInterfaceName']
            apic_em_device_id = host_info['connectedNetworkDeviceId']
            hostname = get_hostname_id(apic_em_device_id, ticket)[0]
            device_type = get_hostname_id(apic_em_device_id, ticket)[1]
            print('The IP address', client_ip, ', is connected to the network device:', hostname, ', model:',
                  device_type, ', interface:', interface_name, ', VLAN:', host_vlan)
    return hostname, interface_name, host_vlan


def check_client_mac_address(client_mac, ticket):
    """
    The function will find out if APIC-EM has a client device configured with the specified MAC address.
    API call to /host
    It will print if a client device exists or not.
    :param client_mac: client MAC address
    :param ticket: APIC-EM ticket
    :return: None
    """

    url = EM_URL + '/host'
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    payload = {'hostMac': client_mac}
    host_response = requests.get(url, params=payload, headers=header, verify=False)
    host_json = host_response.json()

    if not host_json['response']:
        print('The MAC address', client_mac, 'is not used by any client devices')
    else:

        # verification if format of MAC address is correct
        # if MAC address is formatted correct, the 'response' is a list, with one item
        # if MAC address is incorrect formatted, the 'response' is a dictionary, with the error messages

        if type(host_json['response']) is list:
            print('The MAC address', client_mac, 'is used by a client device')
            host_info = host_json['response'][0]
            host_type = host_info['hostType']
            host_vlan = host_info['vlanId']
            host_ip = host_info['hostIp']

            # verification required for wireless clients, JSON output is different for wireless vs. wired clients

            if host_type == 'wireless':

                # info for wireless clients

                apic_em_device_id = host_info['connectedNetworkDeviceId']
                hostname = get_hostname_id(apic_em_device_id, ticket)[0]
                device_type = get_hostname_id(apic_em_device_id, ticket)[1]
                print('The MAC address', client_mac, ', is connected to the network device:', hostname, ', model:',
                      device_type, ', interface VLAN:', host_vlan)
            else:

                # info for ethernet connected clients

                interface_name = host_info['connectedInterfaceName']
                apic_em_device_id = host_info['connectedNetworkDeviceId']
                hostname = get_hostname_id(apic_em_device_id, ticket)[0]
                device_type = get_hostname_id(apic_em_device_id, ticket)[1]
                print('The MAC address', client_mac, ', is connected to the network device:', hostname, ', model:',
                      device_type, ', interface:', interface_name, ', VLAN:', host_vlan)
            print('The client with the MAC address', client_mac, 'has the IP address:', host_ip)
        else:
            print('The MAC address', client_mac, 'is not in correct format')


def get_interface_name(interface_ip, ticket):
    """
    The function will find out if APIC-EM has a network device with the specified IP address configured on an interface
    API call to /interface/ip-address/{ipAddress}, gets list of interfaces with the given IP address.
    The JSON response is different for wireless AP's comparing with switches and routers.
    There is a nested function, get_hostname_ip , to find out the information about wireless
    AP's based on the management IP address
    :param interface_ip: IP address to check
    :param ticket: APIC-EM ticket
    :return: network device hostname
    """

    url = EM_URL + '/interface/ip-address/' + interface_ip
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    interface_info_response = requests.get(url, headers=header, verify=False)
    if not interface_info_response:
        device_ip = interface_ip
        url = 'https://' + EM_URL + '/network-device/ip-address/' + device_ip  # verification required by
        # wireless AP's IP address
        header = {'accept': 'application/json', 'X-Auth-Token': ticket}
        device_info_response = requests.get(url, headers=header, verify=False)
        if not device_info_response:
            print('The IP address ', interface_ip, ' is not configured on any network devices')
        else:
            hostname = get_hostname_ip(device_ip, ticket)[0]
            device_type = get_hostname_ip(device_ip, ticket)[1]
            print('The IP address ', device_ip, ' is configured on network device ', hostname, ',  ', device_type)
            return hostname
    else:
        interface_info_json = interface_info_response.json()
        interface_info = interface_info_json['response'][0]
        interface_name = interface_info['portName']
        device_id = interface_info['deviceId']
        hostname = get_hostname_id(device_id, ticket)[0]
        device_type = get_hostname_id(device_id, ticket)[1]
        print('The IP address ', interface_ip, ' is configured on network device ', hostname, ',  ',
              device_type, ',  interface ', interface_name)
        return hostname


def get_license_device(device_id, ticket):
    """
    The function will find out the active licenses of the network device with the specified device ID
    API call to /license-info/network-device/{id}
    :param device_id: APIC-EM network device id
    :param ticket: APIC-EM ticket
    :return: license information for the device, as a list with all licenses
    """

    license_info = []
    url = EM_URL + '/license-info/network-device/' + device_id
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    payload = {'deviceid': device_id}
    device_response = requests.get(url, params=payload, headers=header, verify=False)
    if device_response.status_code == 200:
        device_json = device_response.json()
        device_info = device_json['response']
        # pprint(device_info)    # use this for printing info about each device
        for licenses in device_info:
            try:  # required to avoid errors due to some devices, for example Access Points,
                # that do not have an "inuse" license.
                if licenses.get('status') == 'INUSE':
                    new_license = licenses.get('name')
                    if new_license not in license_info:
                        license_info.append(new_license)
            except:
                pass
    return license_info


def sync_device(device_name, ticket):
    """
    This function will sync the device configuration from the device with the name {device_name}
    API call to /network-device/sync
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


def create_path_trace(src_ip, dest_ip, ticket):
    """
    This function will create a new Path Visualisation between the source IP address {src_ip} and the
    destination IP address {dest_ip}
    API call to /flow-analysis
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


def get_path_trace_info(path_id, ticket):
    """
    This function will return the path visualisation details for the APIC-EM path visualisation {path_id}
    API call to /flow-analysis/{path_id}
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


def delete_path_trace(path_id, ticket):
    """
    This function will delete the path visualisation with the {path_id}
    API call to /flow-analysis/{path_id}
    :param path_id: APIC-EM path visualisation id
    :param ticket: APIC-EM ticket
    :return: Status code - 202 - deleted
    """

    url = EM_URL + '/flow-analysis/' + path_id
    header = {'accept': 'application/json', 'content-type': 'application/json', 'X-Auth-Token': ticket}
    path_response = requests.delete(url, headers=header, verify=False)
    path_status_code = path_response.status_code
    return path_status_code

