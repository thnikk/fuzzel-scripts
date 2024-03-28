#!/usr/bin/python3 -u
"""
Description: Open SSH session in terminal
Author: thnikk
"""
from subprocess import Popen, PIPE
import sys
import json
import os


def notify(subject, body):
    """ Create notification """
    print(body)
    # pylint: disable=consider-using-with
    Popen(['notify-send', subject, body])


def get_selection(input_list, prompt="", max_lines=8) -> str:
    """ Get selection from list with custom prompt """
    length = str(min(len(input_list), max_lines))
    with Popen(
        ["fuzzel", "--dmenu", "-l", length, "-p", prompt],
        stdin=PIPE, stdout=PIPE, stderr=PIPE
    ) as fuzzel:
        selection = fuzzel.communicate(
            input=bytes("\n".join(input_list), 'utf-8'))[0]
        if fuzzel.returncode != 0:
            sys.exit(1)
        return selection.decode().strip()


def main():
    """ Main function """
    config_file = os.path.expanduser('~/.config/fuzzel/fuzzel-ssh.json')
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = json.loads(file.read())
    except FileNotFoundError:
        with open(config_file, 'w', encoding='utf-8') as file:
            ex_config = {'nickname': 'user@IP'}
            file.write(json.dumps(ex_config))
            notify('fuzzel-ssh', f'Default config created in {config_file}, '
                   'please edit before running again.')
            sys.exit(1)

    selection = get_selection(list(config))
    # pylint: disable=consider-using-with
    Popen(['wezterm', 'ssh', config[selection]])


if __name__ == "__main__":
    main()
