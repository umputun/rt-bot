FROM golang:alpine

ADD . /go/src/github.com/umputun/rt-bot/gif-bot
RUN apk --update add ca-certificates
RUN \
 cd /go/src/github.com/umputun/rt-bot/gif-bot && \
 go build -o /srv/gif-bot && \
 rm -rf /go/src/*

EXPOSE 8080
WORKDIR /srv
CMD ["/srv/gif-bot"]