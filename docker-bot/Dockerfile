FROM ruby:2.4-rc-onbuild
ADD Gemfile .
ADD Gemfile.lock .
ADD Rakefile .
RUN bundle install
RUN rake db:create
EXPOSE "8080"
CMD ["bundle", "exec", "puma", "-p", "8080", "-e", "production"]
