FROM ubuntu:14.04
ENV BUILD_DATE=10_05_2016
ENV TERM=xterm
RUN apt-get update
RUN apt-get install -y software-properties-common python-software-properties curl
RUN curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
RUN apt-get install -y nodejs git git-core gcc make build-essential
RUN npm install -g nodemon mocha
ENV NODE_PATH=.:/usr/lib/node_modules:/node_modules
ADD ./package.json /package.json
RUN mkdir -p /node_modules
RUN npm install --prefix /
ADD ./app /app
WORKDIR /app

EXPOSE 8080
CMD ["node", "/app/app.js"]