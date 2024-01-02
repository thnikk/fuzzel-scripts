#!/usr/bin/env sh

# Get a list of VMs
VMS="$(virsh list --all --name | sed -r '/^\s*$/d' | grep '\-pt')"
# Get the number of VMs
COUNT="$(echo "$VMS" | wc -l)"

# Get a user selection for a VM
SELECTION="$(echo "$VMS" | fuzzel --dmenu -p "Select a VM: " -l "$COUNT")"
[ -z "$SELECTION" ] && exit 1

# Check if the VM is running
RUNNING="$(virsh list --name | sed -r '/^\s*$/d')"

# If it's running, prompt for a selection
if [ "$RUNNING" = "$SELECTION" ]; then
	OPTION="$(printf "shutdown\nreboot\ndestroy" | fuzzel --dmenu -p "Select an option: " -l 3)"
	[ -z "$OPTION" ] && exit 1
# Otherwise, start the VM
else
	OPTION="start"
fi

# Do the thing
virsh "$OPTION" "$SELECTION"
