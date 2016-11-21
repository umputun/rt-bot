FROM java:8-alpine
MAINTAINER Mike Shemanskiy <mike.shemanskiy@gmail.com>

ENV M2_HOME=/usr/lib/mvn
ENV M2=$M2_HOME/bin
ENV PATH $PATH:$JAVA_HOME:$JAVA:$M2_HOME:$M2

ADD http://ftp.fau.de/apache/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz /tmp/

RUN cd /tmp/ && \
    tar -zxvf apache-maven-3.3.9-bin.tar.gz && \
    rm apache-maven-3.3.9-bin.tar.gz && \
    mv apache-maven-3.3.9 /usr/lib/mvn && \
    rm -rf /tmp/* && \
    mkdir -p /bot

ADD . /src
WORKDIR /bot

RUN cd /src/ && mvn -q package \
    && mv target/rtbot-0.0.1-SNAPSHOT.jar /bot \
    && rm -rf /src /usr/lib/mvn /tmp/*

EXPOSE 8080

CMD ["java", "-jar", "rtbot-0.0.1-SNAPSHOT.jar"]
