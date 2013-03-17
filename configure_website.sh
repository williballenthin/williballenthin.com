#!/bin/bash

CD=$(readlink -f .);
CCD=$(echo -n "$CD" | sed -e "s/\//\\\\\\//g");

echo "CD: $CD"
echo "CCD: $CCD"

git submodule init;
git submodule update;

sed -i \
 -e "s/^template .*$/template "$CCD"\/rawdog\/page.template/g" \
 -e "s/^itemtemplate .*$/itemtemplate "$CCD"\/rawdog\/item.template/g" \
 "./rawdog/config";

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
 "./octopress/_config.yml";

if grep -q "^logo:" "./octopress/_config.yml"; then
    sed -i \
      -e "s/^logo:.*$/logo: \/img\/logo.png/g" \
      -e "s/^favicon:.*$/favicon: \/img\/favicon.ico/g" \
      "./octopress/_config.yml";
else
    cat >> "./octopress/_config.yml" <<EOF
# ----------------------- #
#      Theme Resources    #
# ----------------------- #
logo: /img/logo.png
favicon: /img/favicon.ico
EOF
fi

rm -r "$CD/octopress/source";
ln -s "$CD/octopress_site_source" "$CD/octopress/source";

pushd "./octopress/";
if [ ! -e "./.themes/williballenthin-octopress-theme" ]; then
    pushd ".themes";
    ln -s "$(pwd)/../../williballenthin-octopress-theme" "williballenthin-octopress-theme";
fi
rake install[williballenthin-octopress-theme];
popd;
