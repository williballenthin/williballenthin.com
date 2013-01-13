#!/bin/bash

sed -i \
 -e "s/^url:.*$/url: http:\/\/www.williballenthin.com/g" \
 -e "s/^title:.*$/title: williballenthin.com/g" \
 -e "s/^subtitle:.*$/subtitle:/g" \
 -e "s/^author:.*$/author: Willi Ballenthin/g" \
 -e "s/^source:.*$/source: source/g" \
 -e "s/^github_user:.*$/github_user: williballenthin/g" \
 -e "s/^github_repo_count:.*$/github_repo_count: 5/g" \
 -e "s/^twitter_user:.*$/twitter_user: williballenthin/g" \
 -e "s/^twitter_tweet_button:.*$/twitter_tweet_button: false/g" \
 -e "s/^googleplus_user:.*$/googleplus_user: wilbal1087@gmail.com/g" \
 -e "s/^google_analytics_tracking_id:.*$/google_analytics_tracking_id: UA-23141359-1/g" \
 ./octopress/_config.yml;

CD=$(readlink -f .);
rm -r "$CD/octopress/source";
ln -s "$CD/octopress_site_source" "$CD/octopress/source";

pushd ./octopress/;
rake install;
popd;