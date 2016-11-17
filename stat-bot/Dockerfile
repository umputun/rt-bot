FROM ubuntu:14.04.5

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y build-essential
RUN curl -L http://cpanmin.us | sudo perl - App::cpanminus
RUN cpanm JSON
RUN curl -L https://cpanmin.us | perl - -M https://cpan.metacpan.org -n Mojolicious

WORKDIR /stat-bot

RUN curl -L -O http://download.cdn.yandex.net/mystem/mystem-2.1-linux3.2-64bit.tar.gz
RUN tar -xvf mystem-2.1-linux3.2-64bit.tar.gz
RUN chmod +x mystem

ADD stat-bot.pl /stat-bot
RUN mkdir lib
ADD lib/StatBot.pm /stat-bot/lib

EXPOSE 8080

CMD ["perl", "stat-bot.pl"]