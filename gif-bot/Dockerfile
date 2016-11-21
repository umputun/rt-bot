FROM golang:alpine

RUN set -x && \
    apk add --no-cache ca-certificates && \
    rm -rf /var/cache/apk/* /tmp/*

ADD . /go/src/github.com/umputun/rt-bot/gif-bot

RUN \
 cd /go/src/github.com/umputun/rt-bot/gif-bot && \
 go build -o /srv/gif-bot && \
 rm -rf /go/src/*

EXPOSE 8080
WORKDIR /srv
CMD ["/srv/gif-bot"]