
# developed by Gabi Zapodeanu, TSA, GSS, Cisco Systems


# !/usr/bin/env python3


import spark_apis
import utils


# declarations for team/room/membership

SPARK_TEAM_NAME = 'Team1Test'
SPARK_ROOM_NAME = 'Room1Test'
EMAIL = 'gabi@cisco.com'

UTILVAR = [{'fg': '24'},{'25':'ab','356':'df'}]


def main():
    utils.pprint(UTILVAR)
    spark_apis.create_team(SPARK_TEAM_NAME)
    spark_apis.create_room(SPARK_ROOM_NAME, SPARK_TEAM_NAME)
    spark_apis.post_room_message(SPARK_ROOM_NAME, 'Hi are you')
    input('\nTo continue press any key')
    spark_apis.delete_team(SPARK_TEAM_NAME)

if __name__ == '__main__':
        main()


