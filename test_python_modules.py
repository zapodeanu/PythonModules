
# developed by Gabi Zapodeanu, TSA, GPO, Cisco Systems


# !/usr/bin/env python3


import spark_apis
import meraki_apis
import utils
import logging
import sys
import pi_apis

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

UTILVAR = [{'fg': '24'}, {'25': 'ab', '356': 'df'}]


def main():
    """
    The test module will provide the environment to test various Python modules.
    """

    # Testing Spark APIs

    print('\n\n\nTESTING SPARK APIs\n')

    spark_apis.create_team(SPARK_TEAM_NAME)
    spark_apis.create_room(SPARK_ROOM_NAME, SPARK_TEAM_NAME)
    spark_apis.post_room_message(SPARK_ROOM_NAME, 'How are you')
    spark_apis.add_team_membership(SPARK_TEAM_NAME, 'gzapodea@cisco.com')

    input('\nTo continue press any key  ')
    spark_apis.delete_team(SPARK_TEAM_NAME)

    # Testing PI APIs

    print('\n\n\nTESTING PI APIs\n')

    #  deploy DC router CLI template

    dc_device_hostname = 'PDX-RO'
    pi_dc_device_id = pi_apis.pi_get_device_id(dc_device_hostname)
    print('Head end router: ', dc_device_hostname, ', PI Device id: ', pi_dc_device_id)

    # this is the CLI text config file
    dc_file_name = 'GRE_DC_Config.txt'
    print('DC CLI text file name is: ', dc_file_name)

    dc_cli_template_name = dc_file_name.split('.')[0]
    print('DC CLI template name is: ', dc_cli_template_name)

    variables_list = None

    # upload the new CLI config file to PI
    dc_cli_template_id = pi_apis.pi_upload_cli_template(dc_file_name, dc_cli_template_name, variables_list)
    print('The DC CLI template id is: ', dc_cli_template_id)

    # deploy the new uploaded PI CLI template to the DC router

    variables_value = None
    pi_dc_job_name = pi_apis.pi_deploy_cli_template(pi_dc_device_id, dc_cli_template_name, variables_value)
    print('The PI DC Job CLI template deployment is: ', pi_dc_job_name)

    # check for job status

    print('Wait for PI to complete template deployments')
    time.sleep(45)  # time delay to allow PI de deploy the jobs
    dc_job_status = pi_apis.pi_get_job_status(pi_dc_job_name)
    print('DC CLI template deployment status: ', dc_job_status)


if __name__ == '__main__':
        main()


