#!/bin/bash

mapfile -t SINKS < <(pactl list sinks short | awk -F ' ' '{print $2}')

getIndex(){
    for SINK in "${SINKS[@]}"
    do
        case $SINK in
            *"PnP"*) echo "Speakers";;
            *"Logitech"*) echo "Headphones";;
            *"bluez"*) echo "Bluetooth";;
            *"hdmi"*) echo "Monitor";;
            *) echo "$SINK";;
        esac
    done | fuzzel --dmenu -l "${#SINKS[@]}" --index 2>/dev/null
}

INDEX="$(getIndex)"
#echo "$INDEX"

[ -z "$INDEX" ] && exit 1

NEW_SINK="${SINKS[$INDEX]}"
#echo "$NEW_SINK"

pactl set-default-sink "${NEW_SINK}"
#for i in $(pactl list short sink-inputs | awk '{print $1}'); do
    # Move all sink inputs to new sink
    #echo "Moving $i to $NEW_SINK"
    #pactl move-sink-input "$i" @DEFAULT_SINK@
#done
