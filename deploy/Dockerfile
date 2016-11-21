FROM golang:alpine

ENV DOCKER_HOST unix:///var/run/docker.sock
RUN apk add --update docker py-pip && pip install docker-compose && docker -v

ADD . /go/src/github.com/umputun/rt-bot/deploy
RUN \
 cd /go/src/github.com/umputun/rt-bot/deploy && \
 go get -v && \
 go build -o /srv/deploy && \
 rm -rf /go/src/*

ADD deploy.sh /srv/deploy.sh

EXPOSE 8080
WORKDIR /srv
CMD ["/srv/deploy"]
