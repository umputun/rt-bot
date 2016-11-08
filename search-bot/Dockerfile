FROM golang:alpine

ADD . /go/src/github.com/umputun/rt-bot/search-bot
RUN apk --update add ca-certificates
RUN \
 cd /go/src/github.com/umputun/rt-bot/search-bot && \
 go build -o /srv/search-bot && \
 mkdir /srv/data && \
 rm -rf /go/src/*

EXPOSE 8080
WORKDIR /srv
CMD ["/srv/search-bot"]
