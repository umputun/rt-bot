package com.gekoreed.entity;

public class Response {
    public String text;
    public String bot = "sbot";

    public Response(String s) {
        this.text = s;
    }

    public static Response podcastStarted() {
        return new Response("Начинаю записывать заметки с этого момента.");
    }
}
