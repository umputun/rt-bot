FROM golang:alpine

ADD . /go/src/github.com/umputun/rt-bot/brackets-bot
RUN \
 cd /go/src/github.com/umputun/rt-bot/brackets-bot && \
 go get -v && \
 go build -o /srv/brackets-bot && \
 rm -rf /go/src/*

EXPOSE 8080
WORKDIR /srv
CMD ["/srv/brackets-bot"]
