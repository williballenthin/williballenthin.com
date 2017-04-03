williballenthin.com
===================

Source for my personal website.
Build using Jekyll 3.0.

Theme based on [The Plain v1](https://github.com/heiswayi/the-plain).

tips
----

```
$ docker build -t williballenthin.com/deploy .
$ docker run --rm -it williballenthin.com/deploy
From https://github.com/williballenthin/williballenthin.com
 * branch            master     -> FETCH_HEAD
Already up-to-date.
Configuration file: /code/williballenthin.com/_config.yml
            Source: /code/williballenthin.com/
       Destination: /code/williballenthin.com/_site
 Incremental build: disabled. Enable with --incremental
      Generating...
                    done in 3.54 seconds.
 Auto-regeneration: disabled. Use --watch to enable.
S3_ID: ****
S3_SECRET: ****
[info] Deploying /code/williballenthin.com/_site/* to www.williballenthin.com
[info] Summary: There was nothing to push
```
