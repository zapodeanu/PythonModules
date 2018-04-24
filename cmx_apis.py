
#!/usr/bin/env python3

# developed by Gabi Zapodeanu, TSA, GPO, Cisco Systems


# this module includes common utilized functions to create applications using CMX APIs

import requests
import json
import urllib3

from modules_init import CMX_URL, CMX_USER, CMX_PASSW

from urllib3.exceptions import InsecureRequestWarning

from requests.auth import HTTPBasicAuth  # for Basic Auth

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

CMX_AUTH = HTTPBasicAuth(CMX_USER, CMX_PASSW)


def create_notification(notification_name):
    """
    This function will create a notification with the name {notification_name}
    :param notification_name - notification name
    :return status code for the notification request
    """
    url = CMX_URL + '/api/config/v1/notification'
    print('CMX URL and Resource: ', url)
    payload = {
            "name": notification_name,
            "rules": [
                {
                    "conditions": [
                        {
                            "condition": "inout.deviceType == client"
                        },
                        {
                            "condition": "inout.in/out == in"
                        },
                        {
                            "condition": "inout.hierarchy == DevNetCampus>DevNetBuilding>DevNetZone"
                        }
                    ]
                }
            ],
            "subscribers": [
                {
                    "receivers": [
                        {
                            "uri": "http://128.107.70.29:8010",
                            "messageFormat": "JSON",
                            "qos": "AT_MOST_ONCE"
                        }
                    ]
                }
            ],
            "enabled": True,
            "enableMacScrambling": True,
            "macScramblingSalt": "listening",
            "notificationType": "InOut"
        }
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    notification_response = requests.put(url, data=json.dumps(payload), headers=header, auth=CMX_AUTH, verify=False)
    print('Notification Status Code: ', notification_response.status_code)
    return notification_response.status_code


def all_client_number():
    """
    This function will find out how many wireless clients are visible in the environment
    REST API call to CMX - /api/location/v2/clients/count
    :param
    :return: The total number of clients, associated and not associated with the APs
    """

    url = CMX_URL + '/api/location/v2/clients/count'
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, auth=CMX_AUTH, verify=False)
    response_json = response.json()
    clients_number = response_json['count']
    return clients_number


def get_cmx_map(campus, building, floor, file):
    """
    The function will get the floor map for the floor with the name {floor},
    located in the specified building and campus.
    REST API call to CMX - 'api/config/v1/maps/image/' + campus/building/floor
    :param campus: campus name
    :param building: building name
    :param floor: floor name
    :param file: file name to save the image to
    :return: save the floor map image
    """

    url = CMX_URL + '/api/config/v1/maps/image/' + campus + '/' + building + '/' + floor

    header = {'content-type': 'application/json'}
    response = requests.get(url, headers=header, auth=CMX_AUTH, verify=False)
    print('\nThe floor map request url is: ', url)
    print('Request status code is: ', response.status_code)

    if response.status_code == 200:  # validate if the request was successful
        print('Assignment 2 completed')
    else:
        print('Assignment 2 not completed, please try again')

    # open a file to save the image to

    image_file = open(file, 'wb')
    image_file.write(response.content)  # save the content of the request as it comes back as an image and not JSON
    image_file.close()


def get_cmx_ap_info(campus, building, floor, ap_name):
    """
    The function will get the x/y coordinates of the AP with the name {ap_name} located on
    the floor with the name {floor}, located in the specified building and campus
    :param campus: campus name
    :param building: building name
    :param floor: floor name
    :param ap_name: AP name
    :return: x/y coordinates, from the top left corner of the image
    """

    url = CMX_URL + '/api/config/v1/maps/info/' + campus + '/' + building + '/' + floor
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, auth=CMX_AUTH, verify=False)
    aps_list = response.json()['accessPoints']
    for ap in aps_list:
        if ap['name'] == ap_name:
            ap_x = ap['mapCoordinates']['x']
            ap_y = ap['mapCoordinates']['y']
    return ap_x, ap_y


def get_cmx_ap_mac(campus, building, floor, ap_name):
    """
    The function will get the MAC address of the AP with the name {ap_name} located on
    the floor with the name {floor}, located in the specified building and campus
    :param campus: campus name
    :param building: building name
    :param floor: floor name
    :param ap_name: AP name
    :return: AP mac address
    """

    url = CMX_URL + '/api/config/v1/maps/info/' + campus + '/' + building + '/' + floor
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, auth=CMX_AUTH, verify=False)
    aps_list = response.json()['accessPoints']
    for ap in aps_list:
        if ap['name'] == ap_name:
            ap_mac = ap['radioMacAddress']
    return ap_mac


def all_client_assoc_ap(ap_mac):
    """
    This function will find out how many wireless clients are associated with the AP with the {ap_mac}
    REST API call to CMX - /api/location/v2/clients
    :param ap_mac: The MAC address for the AP
    :return: The total number of clients, associated and not associated with the APs
    """

    url = CMX_URL + '/api/location/v2/clients'
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    response = requests.get(url, headers=header, auth=CMX_AUTH, verify=False)
    clients_json = response.json()
    clients_mac_info = []
    for client in clients_json:
        if client['apMacAddress'] == ap_mac:
            clients_mac_info.append(client['macAddress'])
    return clients_mac_info

