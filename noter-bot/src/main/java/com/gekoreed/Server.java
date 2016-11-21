package com.gekoreed;


import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gekoreed.entity.ChatRequest;
import com.gekoreed.entity.Response;
import com.gekoreed.util.Storage;
import spark.Request;
import spark.Spark;

import java.io.IOException;
import java.time.LocalDateTime;

import static spark.Spark.halt;

public class Server {

    static ObjectMapper mapper = new ObjectMapper();
    Storage storage = new Storage();

    public static void main(String[] args) {
        setServer();
    }

    public static void setServer() {
        Server server = new Server();
        Spark.port(8080);
        Spark.post("/event", (req, resp) -> {
            resp.status(201);
            resp.type("application/json");
            return server.getAnswer(req);
        });
    }

    private String getAnswer(Request req) {
        String body = req.body();
        try {
            JsonNode jsonNode = mapper.readTree(body);
            ChatRequest chatRequest = mapper.convertValue(jsonNode, ChatRequest.class);

            if (chatRequest.startMessage()) {
                storage.setStartTime(LocalDateTime.now());
                return mapper.writeValueAsString(Response.podcastStarted());
            }
            if (!chatRequest.text.startsWith("sbot")) {
                halt(417);
            } else {
                String answer = storage.process(chatRequest);
                Response response = new Response(answer);
                return mapper.writeValueAsString(response);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }

}