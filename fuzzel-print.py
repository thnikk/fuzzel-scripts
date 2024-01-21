#!/usr/bin/python3 -u
"""
Author: thnikk
"""
import urllib.parse as up
import argparse
from subprocess import Popen, PIPE
import requests

parser = argparse.ArgumentParser(
    description="Quick fuzzel moonraker interface")
parser.add_argument('ip', action='store', type=str, help='ip:port')
parser.add_argument('-n', action='store', type=int, help='Number of printers')
parser.add_argument(
    '-f', action="store_true", help='Enable pro and misc filter')
args = parser.parse_args()


def get_fuzzel(input_list, prompt):
    """ Get selection from fuzzel"""
    if len(input_list) < 10:
        length = len(input_list)
    else:
        length = 10
    with Popen(
        ["fuzzel", "--dmenu", "-l", str(length), "-p", prompt],
        stdin=PIPE, stdout=PIPE, stderr=PIPE
    ) as fuzzel:
        selection = fuzzel.communicate(
            input=bytes("\n".join(input_list), 'utf-8'))[0]
        return selection.decode().strip()


def url_append_query(url, dictionary):
    """ Append to querystring """
    parts = up.urlparse(url)
    query_dict = dict(up.parse_qsl(parts.query))
    query_dict.update(dictionary)
    parts = parts._replace(query=up.urlencode(query_dict))
    return up.urlunparse(parts)


def get_filtered_list(server, match):
    """ Get filtered list of printable files """
    file_list_raw = requests.get(
        f"http://{server}/server/files/list", timeout=3).json()
    return [file["path"] for file in file_list_raw["result"]
            if file["path"].startswith(match)]


def get_file_list(server):
    """ Get filtered list of printable files """
    file_list_raw = requests.get(
        f"http://{server}/server/files/list", timeout=3).json()
    return [file["path"] for file in file_list_raw["result"]]


def get_macro_list(server):
    """ Get list of macros """
    file_list_raw = requests.get(
        f"http://{server}/printer/gcode/help", timeout=3).json()
    return list(file_list_raw['result'])


def get_last_file(server):
    """ Get last printed file """
    file = requests.get(f"http://{server}/printer/objects/query?webhooks" +
                        "&virtual_sdcard&print_stats", timeout=3).json()
    return file["result"]["status"]["print_stats"]["filename"]


# Increment port depending on the selection
try:
    NUM = get_fuzzel(
        [str(n) for n in range(1, args.n+1)], "Select printer: ")
    split_ip = args.ip.split(":")
    ip = f"{split_ip[0]}:{int(split_ip[1])+int(NUM)-1}"
except TypeError:
    ip = args.ip

# Make list of operations
operations = [
    "Print", "Reprint", "Cancel",
    "Macro", "Firmware restart", "Klipper restart",
    "Emergency stop"
]
if args.f:
    operations.insert(1, "Print Misc")

# Do actions based on selections
match get_fuzzel(operations, "Select an operation: "):
    case "Print":
        if args.f:
            LIST = get_filtered_list(ip, "pro/")
        else:
            LIST = get_file_list(ip)
        FILE = get_fuzzel(LIST, "Select a file: ")
        URL = url_append_query(
            f"http://{ip}/printer/print/start",
            {"filename": FILE})
        requests.post(URL, timeout=3)
    case "Print Misc":
        LIST = get_filtered_list(ip, "misc/")
        FILE = get_fuzzel(LIST, "Select a file: ")
        URL = url_append_query(
            f"http://{ip}/printer/print/start",
            {"filename": FILE})
        requests.post(URL, timeout=3)
    case "Reprint":
        FILE = get_last_file(ip)
        URL = url_append_query(
            f"http://{ip}/printer/print/start",
            {"filename": FILE})
        requests.post(URL, timeout=3)
    case "Cancel":
        URL = f"http://{ip}/printer/gcode/script?script=CACNCEL_PRINT"
        requests.post(URL, timeout=3)
    case "Macro":
        LIST = get_macro_list(ip)
        MACRO = get_fuzzel(LIST, "Select a macro: ")
        URL = f"http://{ip}/printer/gcode/script?script={MACRO}"
        requests.post(URL, timeout=3)
    case "Firmware restart":
        URL = f"http://{ip}/printer/firmware_restart"
        requests.post(URL, timeout=3)
    case "Klipper restart":
        URL = f"http://{ip}/printer/restart"
        requests.post(URL, timeout=3)
    case "Emergency stop":
        URL = f"http://{ip}/printer/emergency_stop"
        requests.post(URL, timeout=3)
