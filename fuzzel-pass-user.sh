#!/bin/bash

export PASSWORD_STORE_CLIP_TIME=10

shopt -s nullglob globstar

prefix=${PASSWORD_STORE_DIR-~/.password-store}
password_files=( "$prefix"/**/*.gpg )
password_files=( "${password_files[@]#"$prefix"/}" )
password_files=( "${password_files[@]%.gpg}" )

password=$(printf '%s\n' "${password_files[@]}" | fuzzel --dmenu "$@")

[[ -n $password ]] || exit

wl-copy "$(basename "$password")" 2>/dev/null
