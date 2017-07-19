
# developed by Gabi Zapodeanu, TSA, GPO, Cisco Systems


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


if __name__ == '__main__':
        main()


