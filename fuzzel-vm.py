#!/usr/bin/python3 -u
"""
Description: Do VM operations with Fuzzel. This script keeps a cache of which
VMs are opened and puts the most frequently used/active at the top of the list.
Author: thnikk
"""
from subprocess import Popen, PIPE, run
import sys
import json
import os
import argparse

parser = argparse.ArgumentParser(description="VM fuzzel launcher")
parser.add_argument(
    'filter', type=str,
    nargs='*', help="Filter for blacklist")
parser.add_argument('-w', action='store_true',
                    help="Change blacklist to whitelist.")
args = parser.parse_args()


def vm_list() -> list:
    """ Get a list of VMs """
    output = run(
        ["virsh", "list", "--all", "--name"],
        capture_output=True, check=False
    ).stdout.decode('utf-8').strip().splitlines()
    return output


def vm_active() -> list:
    """ Get a list of VMs """
    output = run(
        ["virsh", "list", "--name"],
        capture_output=True, check=False
    ).stdout.decode('utf-8').strip().splitlines()
    return output


def sort_some(all, some) -> list:
    """ Move active VMs to top of list """
    for item in some:
        try:
            all.remove(item)
        except ValueError:
            some.remove(item)
    return some + all


def get_selection(input_list, prompt="") -> str:
    """ Get selection from list with custom prompt """
    length = str(min(len(input_list), 8))
    with Popen(
        ["fuzzel", "--dmenu", "-l", length, "-p", prompt],
        stdin=PIPE, stdout=PIPE, stderr=PIPE
    ) as fuzzel:
        selection = fuzzel.communicate(
            input=bytes("\n".join(input_list), 'utf-8'))[0]
        if fuzzel.returncode != 0:
            sys.exit(1)
        return selection.decode().strip()


def sort_dict(dictionary) -> dict:
    """ Sort dictionary based on values """
    return dict(sorted(dictionary.items(), key=lambda x: x[1], reverse=True))


def filter_list(item_list, filter_strings, invert=False) -> list:
    """ Create list using filter strings as whitelist/blacklist filter """
    # temp_list = []
    # for item in item_list:
    #     for filter_string in filter_strings:
    #         print(filter_string, item, filter_string in item)
    #         if filter_string in item:
    #             temp_list.append(item)
    temp_list = [
        item for item in item_list
        for filter_string in filter_strings
        if filter_string in item
    ]
    if invert:
        return temp_list
    return sorted(list(set(item_list) - set(temp_list)))


def main():
    """ Main function """
    cache_file = os.path.expanduser('~/.cache/fuzzel-vm.json')
    try:
        with open(cache_file, 'r', encoding='utf-8') as file:
            cache = json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        cache = []
    unique = set(cache)
    counted = {item: cache.count(item) for item in unique}
    filtered_list = filter_list(vm_list(), args.filter, args.w)
    sorted_cache = sort_some(filtered_list, list(sort_dict(counted)))
    active = vm_active()
    sorted_active = sort_some(sorted_cache, active)
    selection = get_selection(sorted_active)
    if selection in active:
        operation = get_selection(["shutdown", "reboot", "destroy"],
                                  "Select an option: ")
        run(["virsh", operation, selection], check=False)
    else:
        run(["virsh", "start", selection], check=False)
        cache = ([selection] + cache)[:20]
        with open(cache_file, 'w', encoding='utf-8') as file:
            file.write(json.dumps(cache, indent=4))


if __name__ == "__main__":
    main()
