#!/bin/bash

cat "./_header.template" > "./index.html";
ls -1 | grep "^[0-9][0-9][0-9][0-9]\-[0-9][0-9]\-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.[0-9][0-9][0-9][0-9][0-9][0-9] UTC.html$" | sort -r | sed -e "s/^\(.*\)\.html$/<li><a href=\"\1.html\">\1<\/a><\/li>/g" >> "./index.html";
cat "./_footer.template" >> "./index.html";
