williballenthin.com
===================

Source for my personal website


Layout:
  - app - A Google App Engine application ready to be uploaded. 
  - octopress - A Git submodule that tracks octopress. Don't change anything in it.
  - Use `configure_octopress.sh` to apply the appropriate configuration to octopress to use with this website.
  - Use `deploy_octopress.sh` to configure, generate, and deploy the website using GAE.

Dependencies:
  - GAE appcfg.py is at /home/willi/Tools/google\_appengine/
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
