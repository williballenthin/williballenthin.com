#!/bin/bash

cd /code/williballenthin.com/;
git pull origin master;

mkdir /code/williballenthin.com/_site;
chmod a+w /code/williballenthin.com/_site;
jekyll build --source="/code/williballenthin.com/" --destination="/code/williballenthin.com/_site";

echo -n "S3_ID: ";
read -s S3_ID;
echo "";

echo -n "S3_SECRET: ";
read -s S3_SECRET;
echo "";

S3_ID="$S3_ID" S3_SECRET="$S3_SECRET" s3_website push --site="/code/williballenthin.com/_site";
