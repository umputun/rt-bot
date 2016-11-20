FROM anapsix/alpine-java:8_jdk

ENV M2_HOME=/usr/lib/mvn
ENV M2=$M2_HOME/bin
ENV PATH $PATH:$JAVA_HOME:$JAVA:$M2_HOME:$M2

ADD http://ftp.fau.de/apache/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz /tmp

RUN set -x && \
    tar -xvzf /tmp/apache-maven-3.3.9-bin.tar.gz -C /tmp && \
    mv /tmp/apache-maven-3.3.9 /usr/lib/mvn && \
    rm -rf /tmp/*

RUN mkdir bot
ADD src /bot/src
ADD pom.xml /bot

RUN set -x && \
    cd /bot && \
    mvn install -q dependency:copy-dependencies && \
    mv target/dependency . && \
    mv target/bot.jar . && \
    rm -r target src pom.xml /usr/lib/mvn

WORKDIR /bot

EXPOSE 8080

CMD ["java", "-cp", "bot.jar:./dependency/*:.", "com.gekoreed.Server"]