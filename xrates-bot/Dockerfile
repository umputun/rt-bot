FROM ssgreg/haskell-stack:latest

ADD . /haskell/src/ssgreg/xrates-bot
RUN \
 cd /haskell/src/ssgreg/xrates-bot && \
 stack install --local-bin-path /srv && \
 rm -rf /haskell/src/*

EXPOSE 8080
WORKDIR /srv
CMD ["/srv/xrates-bot"]
