
# developed by Gabi Zapodeanu, TSA, GSS, Cisco Systems


# !/usr/bin/env python3

import requests
import json
import requests.packages.urllib3

from requests_toolbelt import MultipartEncoder  # required to encode messages uploaded to Spark
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from Spark_APIs_init import SPARK_AUTH, SPARK_URL

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings


# declarations for team/room/membership

spark_team_name = 'TeamTest'
spark_room_name = 'RoomTest'
email = 'gabi@cisco.com'



def main():


if __name__ == '__main__':
    main()

