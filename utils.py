# developed by Gabi Zapodeanu, TSA, GSS, Cisco Systems

import json

# !/usr/bin/env python3

def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data:
    :return:
    """

    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))

