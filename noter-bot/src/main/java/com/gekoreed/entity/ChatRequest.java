package com.gekoreed.entity;

public class ChatRequest {
    public String text;
    public String username;
    public String display_name;

    public boolean startMessage() {
        return (display_name.equalsIgnoreCase("радио-т бот") 
                || username.equalsIgnoreCase("радио-т бот"))
                && text.contains("Официальный кат!");
    }
}
