FROM golang:alpine

RUN apk add --no-cache ca-certificates

ADD . /go/src/github.com/umputun/rt-bot/search-bot

RUN \
 cd /go/src/github.com/umputun/rt-bot/search-bot && \
 go build -o /srv/search-bot && \
 mkdir /srv/data && \
 rm -rf /go/src/*

EXPOSE 8080
WORKDIR /srv
CMD ["/srv/search-bot"]
