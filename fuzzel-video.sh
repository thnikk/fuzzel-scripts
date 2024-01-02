#!/usr/bin/env sh
# This is a generic fuzzel launcher that will list all files in a file or directory 
# with all tags stripped from the name and open the selected file in MPV.

# Cache file containing a file list generated every 5 minutes on the server to save time
if [ -d "$1" ]; then
	FILELIST="$(find -L "$1" -printf "%T+\t%p\n" | sort -r | grep "mkv\|mp4\|mov\|avi" | awk -F '\t' '{print $NF}' 2>/dev/null)"
elif [ -f "$1" ]; then
	FILELIST="$(cat "$1")"
else
	echo "Please enter valid cache file or directory"
	exit 1
fi

# Sed breakdown:
# s!.*/!! is basically basename using sed
# s/\[[^][]*\]//g removes brackets and contents
# s/([^()]*)//g removes parentheses and contents
# s/\..*// removes the file extension
# s/_/ /g replaces underscores with spaces
# s/^ *//g removes leading spaces
# s/ *$//g removes trailing spaces 

# Fuzzel returns the index, so we can easily find the full filename based on the selection 
INDEX="$( echo "$FILELIST" | sed 's!.*/!!;s/\[[^][]*\]//g;s/([^()]*)//g;s/\.[^.]*$//;s/_/ /g;s/^ *//g;s/ *$//g' | fuzzel --dmenu --index 2>/dev/null)"

# Quit if the index doesn't exist (exited out of fuzzel) or increment by 1
[ -z "$INDEX" ] && exit || INDEX=$(( INDEX + 1 ))

# Get the file from the index using sed
SELECTION="$(echo "$FILELIST" | sed "${INDEX}q;d")"

# Add profile to command for given directory
echo "$SELECTION" | grep -i "anime" && PROFILE="--profile=anime" && echo "Yes"

# Launch mpv
mpv "$PROFILE" "${SELECTION}" >/dev/null
