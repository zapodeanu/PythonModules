# developed by Gabi Zapodeanu, TSA, GSS, Cisco Systems

# !/usr/bin/env python3

# this module includes common utilized utility functions

import json
import sys
import select


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data:
    :return:
    """

    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def get_input_ip():
    """
    This function will ask the user to input the IP address. The format of the IP address is not validated
    The function will return the IP address
    :return: the IP address
    """

    ip_address = input('Input the IP address to be validated, (or q to exit) ?  ')
    return ip_address


def get_input_mac():
    """
    This function will ask the user to input the IP address. The format of the IP address is not validated
    The function will return the IP address
    :return: the IP address
    """

    mac_address = input('Input the MAC address to be validated, (or q to exit) ?  ')
    return mac_address


def get_input_timeout(message, time):
    """
    This function will ask the user to input the value requested in the {message}, in the time specified {time}
    :param message: message to provide the user information on what is required
    :param time: time limit for the user input
    :return: user input as string
    """

    print(message + ' in ' + str(time) + ' seconds')
    i, o, e = select.select([sys.stdin], [], [], time)

    if i:
        input_value = sys.stdin.readline().strip()
    else:
        input_value = None
    return input_value
