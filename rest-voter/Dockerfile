FROM openjdk:8

RUN mkdir /rest-voter

COPY . /rest-voter

WORKDIR /rest-voter

RUN chmod 777 /rest-voter/gradlew

EXPOSE 8080

RUN ./gradlew build

CMD ["./gradlew", "bootRun"]