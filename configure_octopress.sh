#!/bin/bash

git submodule init;
git submodule update;

sed -i \
 -e "s/^url:.*$/url: http:\/\/www.williballenthin.com/g" \
 -e "s/^title:.*$/title: williballenthin.com/g" \
 -e "s/^subtitle:.*$/subtitle:/g" \
 -e "s/^author:.*$/author: Willi Ballenthin/g" \
 -e "s/^source:.*$/source: source/g" \
 -e "s/^email:.*$/email: willi.ballenthin@gmail.com/g" \
 -e "s/^subscribe_rss:.*$/subscribe_rss:/g" \
 -e "s/^titlecase:.*$/titlecase: false/g" \
 -e "s/^github_user:.*$/github_user: williballenthin/g" \
 -e "s/^github_repo_count:.*$/github_repo_count: 5/g" \
 -e "s/^twitter_user:.*$/twitter_user: williballenthin/g" \
 -e "s/^twitter_tweet_button:.*$/twitter_tweet_button: false/g" \
 -e "s/^googleplus_user:.*$/googleplus_user: wilbal1087@gmail.com/g" \
 -e "s/^googleplus_hidden:.*$/googleplus_hidden: true/g" \
 -e "s/^google_analytics_tracking_id:.*$/google_analytics_tracking_id: UA-23141359-1/g" \
 ./octopress/_config.yml;

if grep -q "^logo:" ./octopress/_config.yml; then
    sed -i \
      -e "s/^logo:.*$/logo: \/img\/logo.png/g" \
      -e "s/^favicon:.*$/favicon: \/img\/favicon.ico\/g" \
      ./octopress/_config.yml;
else
    cat <<EOF
# ----------------------- #
#      Theme Resources    #
# ----------------------- #
logo: /img/logo.png
favicon: /img/favicon.ico
EOF
fi


CD=$(readlink -f .);
rm -r "$CD/octopress/source";
ln -s "$CD/octopress_site_source" "$CD/octopress/source";

pushd ./octopress/;
if [ ! -d ./.themes/williballenthin-octopress-theme ]; then
    pushd .themes;
    git clone git@github.com:williballenthin/williballenthin-octopress-theme.git williballenthin-octopress-theme;
    popd;
else
    pushd .themes/williballenthin-octopress-theme;
    git pull origin master;
    popd;
fi
rake install[williballenthin-octopress-theme];
popd;
