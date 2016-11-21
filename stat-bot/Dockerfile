FROM perl:5

ADD http://download.cdn.yandex.net/mystem/mystem-2.1-linux3.2-64bit.tar.gz /tmp/mystem.tar.gz

RUN cpanm Mojolicious JSON

COPY . /stat-bot
WORKDIR /stat-bot

RUN set -x && \
    tar -xvf /tmp/mystem.tar.gz && \
    chmod +x mystem && \
    rm -rf /tmp/*

EXPOSE 8080

CMD ["perl", "stat-bot.pl"]
