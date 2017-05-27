
# developed by Gabi Zapodeanu, TSA, GSS, Cisco Systems


# !/usr/bin/env python3



import spark_apis
import meraki_apis
import utils
import logging
import sys

import json
import select
import requests
import time
import requests.packages.urllib3
import PIL
import os
import os.path


from PIL import Image, ImageDraw, ImageFont
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth  # for Basic Auth

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings


# declarations for team/room/membership

SPARK_TEAM_NAME = 'Team1Test'
SPARK_ROOM_NAME = 'Room1Test'
EMAIL = 'gabi@cisco.com'

MERAKI_ORG_NAME = 'GZ'
MERAKI_NETWORK = 'APIsDemo'
MERAKI_SSID = 'Guest'

UTILVAR = [{'fg': '24'},{'25':'ab','356':'df'}]


def main():
    """
    The test modules could be rub in demo more, printing output to console, or logging all debug level messages
    to a file python_modules.log.
    Enter 'y' to run in demo mode within 10 seconds from the 'run' command
    :return: 
    """

    # save the initial stdout
    initial_sys = sys.stdout

    user_input = utils.get_input_timeout('If running in Debugging Mode please enter  y ', 5)

    # this section will determine if running the code in demo mode or logging debug to a file

    if user_input == 'y':

        # open a log file 'python_modules.log'
        file_log = open('python_modules.log', 'w')

        # open an error log file 'python_modules_err.log'
        err_log = open('python_modules_err.log', 'w')

        # redirect the stdout to file_log and err_log
        sys.stdout = file_log
        sys.stderr = err_log

        # configure basic logging to send to stdout, level DEBUG, include timestamps
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format=('%(asctime)s - %(levelname)s - %(message)s'))


    # Testing Spark APIs

    # print('\n\n\nTESTING SPARK APIs\n')

    #spark_apis.create_team(SPARK_TEAM_NAME)
    #spark_apis.create_room(SPARK_ROOM_NAME, SPARK_TEAM_NAME)
    #spark_apis.post_room_message(SPARK_ROOM_NAME, 'How are you')
    #spark_apis.add_team_membership(SPARK_TEAM_NAME, 'gabriel.zapodeanu@gmail.com')

    #input('\nTo continue press any key  ')
    #spark_apis.delete_team(SPARK_TEAM_NAME)


    # Testing Meraki APIs

    print('\n\n\nTESTING MERAKI APIs\n')

    meraki_organizations = meraki_apis.get_organizations()
    print('\nMeraki organizations for the user with the MERAKI_API_KEY:')
    utils.pprint(meraki_organizations)

    meraki_organization_id = meraki_apis.get_organization_id(MERAKI_ORG_NAME)
    print('\nMeraki organization id for the organization name ', MERAKI_ORG_NAME, ' :', meraki_organization_id)

    meraki_networks = meraki_apis.get_networks(MERAKI_ORG_NAME)
    print('\nMeraki networks for the Meraki organization name ', MERAKI_ORG_NAME, ' :')
    utils.pprint(meraki_networks)

    meraki_network_id = meraki_apis.get_network_id(MERAKI_ORG_NAME,MERAKI_NETWORK)
    print('\nMeraki network id for the Meraki network name ', MERAKI_NETWORK, ' : ', meraki_network_id)

    meraki_sm_devices = meraki_apis.get_sm_devices(MERAKI_ORG_NAME, MERAKI_NETWORK)
    print('\nMeraki SM devices : ')
    utils.pprint(meraki_sm_devices)

    meraki_network_devices = meraki_apis.get_network_devices(MERAKI_ORG_NAME, MERAKI_NETWORK)
    print('\nMeraki network devices : ')
    utils.pprint(meraki_network_devices)

    meraki_ssids=meraki_apis.get_ssids(MERAKI_ORG_NAME, MERAKI_NETWORK)
    print('\nMeraki SSIDs : ')
    utils.pprint(meraki_ssids)

    meraki_ssid_status = meraki_apis.enable_ssid(MERAKI_ORG_NAME, MERAKI_NETWORK, MERAKI_SSID)
    print('\nMeraki SSID ', MERAKI_SSID, ' status', meraki_ssid_status)

    meraki_ssid_status = meraki_apis.disable_ssid(MERAKI_ORG_NAME, MERAKI_NETWORK, MERAKI_SSID)
    print('\nMeraki SSID ', MERAKI_SSID, ' status', meraki_ssid_status)


    # restore the stdout to initial value
    sys.stdout = initial_sys

    print('\n\nEnd of application run')


if __name__ == '__main__':
        main()


