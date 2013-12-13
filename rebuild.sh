#!/bin/bash

pushd ./octopress/;
rake generate;
popd;
cp -rf ./octopress/public/* "./public/" 2>/dev/null;
