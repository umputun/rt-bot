FROM golang:alpine

ADD . /go/src/github.com/umputun/rt-bot/lucky
RUN \
 cd /go/src/github.com/umputun/rt-bot/lucky && \
 go get -v && \
 go build -o /srv/lucky && \
 rm -rf /go/src/*

EXPOSE 8080
WORKDIR /srv
CMD ["/srv/lucky"]
