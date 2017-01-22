FROM microsoft/dotnet:1.1-sdk-projectjson

ENV ASPNETCORE_ENVIRONMENT Production

RUN mkdir /app
WORKDIR /app
COPY ./Bot4Bots/project.json /app
RUN dotnet restore
COPY ./Bot4Bots /app
RUN dotnet build

EXPOSE 8080/tcp

CMD ["dotnet", "run"]
