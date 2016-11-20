FROM node:7-alpine

ENV NODE_PATH=.:/usr/lib/node_modules:/node_modules

RUN set -x && \
    npm install --silent -g nodemon mocha && \
    mkdir -p /node_modules

COPY ./package.json /package.json
RUN npm install --silent --prefix /

COPY ./app /app
WORKDIR /app

EXPOSE 8080
CMD ["node", "/app/app.js"]
