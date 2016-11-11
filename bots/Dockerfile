FROM golang:alpine

ADD . /go/src/github.com/umputun/rt-bot/bots
RUN \
 cd /go/src/github.com/umputun/rt-bot/bots && \
 go get -v && \
 go build -o /srv/bots && \
 rm -rf /go/src/*

EXPOSE 8080
WORKDIR /srv
CMD ["/srv/bots"]
