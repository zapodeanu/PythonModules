
# developed by Gabi Zapodeanu, TSA, GSS, Cisco Systems


# !/usr/bin/env python3



import spark_apis
import meraki_apis
import utils
import logging
import sys


# declarations for team/room/membership

SPARK_TEAM_NAME = 'Team1Test'
SPARK_ROOM_NAME = 'Room1Test'
EMAIL = 'gabi@cisco.com'

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

    user_input = utils.get_input_timeout('If running in Demo Mode please enter y ', 10)

    if user_input != 'y':

        # open a log file 'python_modules.log'
        file_log = open('python_modules.log', 'w')

        # open an error log file 'python_modules_err.log'
        err_log = open('python_modules_err.log', 'w')

        # redirect the stdout to file_log and err_log
        sys.stdout = file_log
        sys.stderr = err_log

        # configure basic logging to send to stdout, level DEBUG, include timestamps
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format=('%(asctime)s - %(levelname)s - %(message)s'))

    utils.pprint(UTILVAR)

    spark_apis.create_team(SPARK_TEAM_NAME)
    spark_apis.create_room(SPARK_ROOM_NAME, SPARK_TEAM_NAME)
    spark_apis.post_room_message(SPARK_ROOM_NAME, 'How are you')
    spark_apis.add_team_membership(SPARK_TEAM_NAME, 'gabriel.zapodeanu@gmail.com')

    input('\nTo continue press any key  ')
    spark_apis.delete_team(SPARK_TEAM_NAME)

    # restore the stdout to initial value
    sys.stdout = initial_sys

    print('End of application run')


if __name__ == '__main__':
        main()


