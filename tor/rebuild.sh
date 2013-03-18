#!/bin/bash

INPUTDIR="$1";

cat "./_header.template";
ls -1 "$INPUTDIR" | grep "^[0-9][0-9][0-9][0-9]\-[0-9][0-9]\-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.[0-9][0-9][0-9][0-9][0-9][0-9] UTC.html$" | sort -r | sed -e "s/^\(.*\)\.html$/<li><a href=\"\1.html\">\1<\/a><\/li>/g";
cat "./_footer.template";
