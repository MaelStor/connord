#!/bin/bash


cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
asciimap -h >/dev/null || exit 1

mkdir -p maps

table=$(sqlite3 ../connord/db/connord.sqlite3 'select longitude,latitude,city,country_code from locations' | sort -t'|' -k 4)
echo "$table" | while IFS='|' read -ra entry; do
  if [[ "${entry[3]}" == "au" ]]; then extra=( -m "f" ); fi
  if [[ "${entry[3]}" == "us" ]]; then extra=( -s 0 ); fi
  if [[ "${entry[3]}" == "fr" ]]; then extra=( -s 1 ); fi
  if [[ "${entry[3]}" == "hk" ]]; then entry[3]=cn; fi
  if [[ "${entry[3]}" == "sg" ]]; then entry[3]=id; fi

	cmd=( asciimap -i 30 -p ${entry[0]} ${entry[1]} "'${entry[2]}'" ${entry[3]} "${extra[@]}" )
  ("${cmd[@]}" > maps/"${entry[3]}_${entry[2]}.map")

  unset extra
done

for f in maps/*; do echo "$f"; xclip -sel c "$f"; read -r next; done
