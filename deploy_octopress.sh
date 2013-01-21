#!/bin/bash

./configure_octopress.sh;
pushd octopress;
rake generate;
popd;
cp -r ./octopress/public/* ./app/static/;
python /home/willi/Tools/google_appengine/appcfg.py update ./app/;
rm -rf ./app/static/*;

