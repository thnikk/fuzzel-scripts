#!/usr/bin/python3 -u
"""
Description: Unified fuzzel game launcher
Author: thnikk
"""
import glob
import os
import sys
import json
from subprocess import Popen, PIPE


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


def run_steam() -> dict:
    """ Run steam game """
    apps = {}
    blacklist = ['proton', 'steam']
    for manifest in glob.glob(
            os.path.expanduser(
            "~/.local/share/Steam/steamapps/appmanifest*.acf")):
        with open(manifest, 'r', encoding='utf-8') as file:
            name = ""
            appid = ""
            for line in file:
                if "name" in line:
                    name = line.split('"')[-2]
                if "appid" in line:
                    appid = line.split('"')[-2]
            in_blacklist = False
            for item in blacklist:
                if item in name.lower():
                    in_blacklist = True
            if not in_blacklist and name and appid:
                apps[name] = ["steam", f"steam://rungameid/{appid}"]
    return apps


def run_heroic(install_dir) -> dict:
    """ Run epic game """
    installed = [
        path.split('/')[-1] for path in glob.glob(
            os.path.expanduser(f'{install_dir}/*'))]
    apps = {}
    for library in glob.glob(os.path.expanduser(
        "~/.config/heroic/store_cache/*_library.json"
    )):
        try:
            with open(library, 'r', encoding='utf-8') as file:
                library = json.load(file)
                for game in library['library']:
                    if game['folder_name'] in installed:
                        apps[game['title']] = \
                            ["xdg-open", f"heroic://launch/{game['runner']}"
                                f"/{game['app_name']}"]
        except KeyError:
            pass
    return apps


def run_yuzu(game_dir):
    """ Run yuzu game"""
    games = {}
    if not os.path.isdir(game_dir):
        print("Path does not exist.", file=sys.stderr)
        sys.exit(1)
    for path in glob.glob(f"{game_dir}/*"):
        game_name = path.split("/")[-1].split(".")[0]
        if ".nsp" in path:
            games[game_name.split(
                "[")[0].split("(")[0].replace('_', ' ').rstrip()] = path
        else:
            files = {
                item: os.path.getsize(item) for item in glob.glob(f"{path}/*")}
            try:
                games[game_name] = ["yuzu", "-f", "-g", sorted(files)[0]]
            except IndexError:
                pass
    return games


def sort_dict(dictionary) -> dict:
    """ Sort dictionary based on values """
    return dict(sorted(dictionary.items(), key=lambda x: x[1], reverse=True))


def get_frequent(cache_file) -> list:
    """ Get ordered list """
    try:
        with open(cache_file, 'r', encoding='utf-8') as file:
            cache = json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        cache = []
    unique = set(cache)
    counted = {item: cache.count(item) for item in unique}
    return list(sort_dict(counted))


def sort_some(full, some) -> list:
    """ Move active VMs to top of list """
    for item in some:
        try:
            full.remove(item)
        except ValueError:
            some.remove(item)
    return some + full


def main() -> None:
    """ Load launcher from config """
    config_path = os.path.expanduser("~/.config/fuzzel/fuzzel-game.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        config = {
            "Steam": {"enable": True},
            "Heroic": {"enable": True, "path": "~/Games"},
            "Yuzu": {"enable": False, "path": "/mnt/server2/Games/NSP"},
            "Genshin Impact": {
                "enable": True,
                "command": ["an-anime-game-launcher", "--run-game"]},
            "Honkai Star Rail": {
                "enable": False,
                "command": ["the-honkers-railway-launcher", "--run-game"]}
        }
        with open(config_path, 'w', encoding='utf-8') as config_file:
            config_file.write(json.dumps(config, indent=4))
            Popen(
                [
                    "fuzzel", "--dmenu", "-l", "0", "-p",
                    "Config created, please "
                    "edit ~/.config/fuzzel/fuzzel-game.json"])
            sys.exit(1)

    games = {}
    for launcher, settings in config.items():
        if settings["enable"]:
            match launcher:
                case "Steam":
                    games.update({
                        f"{item} [steam]": command for item, command in
                        run_steam().items()})
                case "Heroic":
                    games.update({
                        f"{item} [heroic]": command for item, command in
                        run_heroic(config[launcher]['path']).items()})
                case "Yuzu":
                    games.update({
                        f"{item} [yuzu]": command for item, command in
                        run_yuzu(config[launcher]['path']).items()})
                case _:
                    games.update(
                        {f"{launcher} [custom]": config[launcher]['command']}
                    )

    cache_file = os.path.expanduser('~/.cache/fuzzel-game.json')
    frequent = get_frequent(cache_file)
    games_list = sort_some(list(games), frequent)
    selection = get_selection(games_list)
    try:
        with open(cache_file, 'r+', encoding='utf-8') as file:
            cache = json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        cache = []
    cache = ([selection] + cache)[:20]
    with open(cache_file, 'w', encoding='utf-8') as file:
        file.write(json.dumps(cache))
    Popen(games[selection])


if __name__ == "__main__":
    main()
