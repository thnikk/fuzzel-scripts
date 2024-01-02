#!/usr/bin/env sh

directory="/run/media/thnikk"
removable="$(ls "$directory")"
lines="$(ls "$directory" | wc -l)"

[ "$lines" = "0" ] && notify-send "No removable drives mounted." && exit 1

selection="$(echo "$removable" | fuzzel --dmenu -l "$lines")"

[ -z "$selection" ] && exit 1

umount "${directory}/${selection}"
