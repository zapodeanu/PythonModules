

# developed by Gabi Zapodeanu, TSA, GPO, Cisco Systems


# !/usr/bin/env python3


import time

import requests.packages.urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import apic_em_apis  # import the APIC-EM module
import utils  # import the utils module
from modules_init import EM_USER, EM_PASSW  # import the APIC-EM username and password

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings


def main():
    """
    The script will create an APIC-EM path trace using the Cisco DevNet Sandbox: https://sandboxapicem.cisco.com/.
    We will retrieve the path trace details and ask the user if to delete the created path trace at the end.
    APIC-EM url, username and password are configured in the modules_init module.
    Change these variables if needed to test with a different controller.
    The code will use functions included with the apic_em_apis module.

    Source IP address: 10.1.15.117
    Destination IP address: 10.2.1.22
    """

    # declarations for source and destination IP addresses,
    # change these variables if needed to test with different IP addresses

    src_ip = '10.1.15.117'
    dest_ip = '10.2.1.22'

    # testing APIC-EM Path Trace APIs

    print('\n\n\nPath Trace APIC-EM APIs\n')

    # create an APIC-EM ticket

    apic_em_ticket = apic_em_apis.get_service_ticket(EM_USER, EM_PASSW)
    print('\nAPIC-EM ticket: ', apic_em_ticket)

    # create a path trace between the source and destination IP addresses

    path_trace_id = apic_em_apis.create_path_trace(src_ip, dest_ip, apic_em_ticket)
    print('\nAPIC-EM Path Trace id created: ', path_trace_id)

    # wait 10 seconds for the path trace to complete

    print('\nWait 10 seconds for the Path Trace to complete')
    time.sleep(10)

    # retrieve the path trace details

    path_trace = apic_em_apis.get_path_trace_info(path_trace_id, apic_em_ticket)
    print('\nPath Trace details: \n')
    utils.pprint(path_trace)

    # optional step to delete the path trace

    user_input = input('\nDo you want to delete the created Path Trace (y/n) ')
    if user_input == 'y':
        delete_path_trace = apic_em_apis.delete_path_trace(path_trace_id, apic_em_ticket)
        if delete_path_trace == 202:
            print('\nPath Trace deleted')

    print('\n\nEnd of Application Run\n')


if __name__ == '__main__':
    main()


