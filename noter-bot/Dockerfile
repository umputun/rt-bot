FROM anapsix/alpine-java:8_jdk

RUN mkdir bot
ADD src /bot/src
ADD pom.xml /bot

RUN wget http://ftp.fau.de/apache/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz
RUN tar -zxvf apache-maven-3.3.9-bin.tar.gz
RUN rm apache-maven-3.3.9-bin.tar.gz
RUN mv apache-maven-3.3.9 /usr/lib/mvn

ENV M2_HOME=/usr/lib/mvn
ENV M2=$M2_HOME/bin
ENV PATH $PATH:$JAVA_HOME:$JAVA:$M2_HOME:$M2

RUN cd /bot \
    && mvn install dependency:copy-dependencies \
    && mv target/dependency . \
    && mv target/bot.jar . \
    && rm -r target src pom.xml /usr/lib/mvn

WORKDIR /bot

EXPOSE 8080

CMD ["java", "-cp", "bot.jar:./dependency/*:.", "com.gekoreed.Server"]