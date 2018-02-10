FROM golang:alpine

ADD . /go/src/github.com/umputun/rt-bot/pirate-bot
RUN \
 cd /go/src/github.com/umputun/rt-bot/pirate-bot && \
 go get -v && \
 go build -o /srv/pirate-bot && \
 rm -rf /go/src/*

EXPOSE 8080
WORKDIR /srv
CMD ["/srv/pirate-bot"]