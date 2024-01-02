#!/usr/bin/env sh

# Config file
CONFIG="$HOME/.config/streamers"

# Get selection
SELECTION="$(fuzzel --dmenu -l "$(wc -l "$CONFIG")" < "$CONFIG")"

# Start player if selection isn't empty
[ -z "$SELECTION" ] || streamlink --player mpv "https://www.twitch.tv/$SELECTION" best || notify-send "Stream is offline"
