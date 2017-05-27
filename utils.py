# developed by Gabi Zapodeanu, TSA, GSS, Cisco Systems

# !/usr/bin/env python3

# this module includes common utilized utility functions

import json
import sys
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


def get_input_timeout(message, wait_time):
    """
    This function will ask the user to input the value requested in the {message}, in the time specified {time}
    :param message: message to provide the user information on what is required
    :param wait_time: time limit for the user input
    :return: user input as string
    """

    print(message + ' in ' + str(wait_time) + ' seconds')
    i, o, e = select.select([sys.stdin], [], [], wait_time)
    if i:
        input_value = sys.stdin.readline().strip()
        print('User input: ', i)
    else:
        input_value = None
        print('No user input in ', wait_time, ' seconds')
    return input_value


def image_annotate(in_image, out_image, text, color, font_size, x, y):
    """
    The function will annotate an image {image_file}. The {text} will be marked on the image with the {color} at
    coordinate {x,y}. Changing the working directory in the main program is needed prior to calling the function.
    See the example in the first lines of code
    :param in_image: source image file
    :param out_image: destination image file
    :param text: the annotation text
    :param font_size: text font size
    :param color: color
    :param x: x coordinate
    :param y: y coordinate
    :return: none
    """

    # change directory to working directory
    # os.chdir('/Users/gzapodea/PythonCode/...')

    image = Image.open(in_image)  # open image file
    image_width, image_height = image.size  # size of the floor
    draw = ImageDraw.Draw(image)  # edit image to annotate
    fonts_folder = '/Library/Fonts'  # for MAC OS X - folder with the fonts
    arial_font = ImageFont.truetype(os.path.join(fonts_folder, 'Arial Black.ttf'), font_size)  # select the font and size
    draw.text((x,y), text, fill=color, font=arial_font)  # annotate with text
    image.save(out_image,'PNG')  # save new image