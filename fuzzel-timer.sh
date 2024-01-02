#!/usr/bin/env sh

SOUND="$HOME/.config/notifications/alert.ogg"
TIME="$(fuzzel -p "Enter a time in seconds: " -d -l 0)"

sleep "$TIME" && notify-send.sh --replace-file="$HOME/.cache/replace-id" "\ Timer up!" && for i in 1 2 3; do paplay --volume=40000 "$SOUND"; done
