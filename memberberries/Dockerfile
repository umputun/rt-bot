FROM microsoft/dotnet:1.1-sdk-projectjson

ENV ASPNETCORE_ENVIRONMENT Production

RUN mkdir /app
WORKDIR /app
COPY ./project.json /app
RUN dotnet restore
COPY . /app
RUN dotnet build

EXPOSE 8080/tcp

CMD ["dotnet", "run", "--server.urls", "http://*:8080"]
