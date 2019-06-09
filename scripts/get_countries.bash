#!/usr/bin/env bash
curl https://api.nordvpn.com/server 2> /dev/null | python -m json.tool \
        | grep 'flag\|country' | perl -ne 'print unless $seen{$_}++' \
        | sed -E -e 's/^        //' -e 's/("flag": )(".*")/\1\L\2/' -e 's/^"flag": //' \
    -e     's/^"country": //' | sed 's/,/:/;n' | paste - - -d' ' | tr '"' "'" | sort \
        | head -c -2 | sed -e '$a\'
