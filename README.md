williballenthin.com
===================

Source for my personal website


Layout:
  - octopress - A Git submodule that tracks octopress. Don't change anything in it.
  - williballenthin-octopress-theme - A Git submodule that tracks the theme used for this website. Commit there, not here.
  - Use `configure_website.sh` to apply the appropriate configuration to Octopress, and build the website.
  - rawdog - Configuration and templates for a curated set of RSS feeds.
  - tor - A simple application that fetches TOR endpoints and writes to a file. Used here to track them over time.

Dependencies:
  - rake
  - Ruby 1.9.3 with rvm (curl -L https://get.rvm.io | bash -s stable --ruby)
    - curl -L https://get.rvm.io | bash -s stable --ruby
    - rvm install 1.9.3
    - rvm use 1.9.3
    - rvm rubygems latest
  - bundler
    - gem install bundler
    - rbenv rehash    # If you use rbenv, rehash to be able to run the bundle command
    - bundle install
  - rawdog


Hints:
  - use `configure_website.sh` to rebuild and deploy the website.
  - use `rebuild.sh` to regenerate the Octopress resources and deploy them. Run from williballenthin.com/.
