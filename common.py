#!/usr/bin/python3 -u
"""
Description: Common module
Author: thnikk
"""
from subprocess import Popen, PIPE
import sys


def get_selection(input_list, prompt="") -> str:
    """ Get selection from list """
    lines = str(min(len(input_list), 8))
    with Popen(
        ["fuzzel", "--dmenu", "-l", lines, "-p", prompt],
        stdin=PIPE, stdout=PIPE, stderr=PIPE
    ) as fuzzel:
        selection = fuzzel.communicate(
            input=bytes("\n".join(input_list), 'utf-8'))[0]
        if fuzzel.returncode != 0:
            sys.exit(1)
        return selection.decode().strip()
