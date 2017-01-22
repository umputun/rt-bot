FROM golang:alpine

ADD . /bot/
WORKDIR /bot
RUN go build -o bot

EXPOSE 8080
CMD ["/bot/bot"]
