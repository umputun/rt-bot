FROM golang:alpine

ADD . /go/src/github.com/umputun/rt-bot/sample-go
RUN \
 cd /go/src/github.com/umputun/rt-bot/sample-go && \
 go get -v && \
 go build -o /srv/sample-go && \
 rm -rf /go/src/*

EXPOSE 8080
WORKDIR /srv
CMD ["/srv/sample-go"]
