package com.gekoreed.util;


import com.gekoreed.entity.ChatRequest;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class Storage {

    private LocalDateTime startTime = LocalDateTime.now();
    Map<String, Map<String, String>> storage = new ConcurrentHashMap<>();

    public LocalDateTime getStartTime() {
        return startTime;
    }

    public void setStartTime(LocalDateTime startTime) {
        this.startTime = startTime;
    }

    public String process(ChatRequest chatRequest) {
        String[] parts = chatRequest.text.split(" ");
        if (parts.length == 1) {
            return getHelpMessage();
        }
        String res = "";
        switch (parts[1]) {
            case "note":
            case "save":
                res = saveNote(chatRequest);
                break;
            case "list":
                res = list(chatRequest);
                break;
            case "clear":
                storage.remove(chatRequest.username);
                res = "### Твоя история пуста, " + chatRequest.username;
                break;
            default:
                res = getHelpMessage();
        }
        return res;
    }

    private String list(ChatRequest chatRequest) {
        String res = "";
        Map<String, String> story = storage.getOrDefault(chatRequest.username, new HashMap<>());
        if (story.isEmpty()) {
            return "Your story is empty";
        }
        res += "### Вот твоя история, " + chatRequest.username;
        for (Map.Entry<String, String> entry : story.entrySet()) {
            res += "\n * " + (entry.getKey() + " - " + entry.getValue());
        }
        return res;
    }

    private String saveNote(ChatRequest chatRequest) {
        String[] parts = chatRequest.text.split(" ");
        Map<String, String> userStory = storage.getOrDefault(chatRequest.username, new HashMap<>());
        if (parts.length == 2) {
            userStory.put(getTime(), "");
            storage.put(chatRequest.username, userStory);
            return "### " + chatRequest.username + ", ты только что сохранил пустую временную заметку";
        } else {
            String note = "";
            for (int t = 2; t < parts.length; t++) {
                note += parts[t] + " ";
            }
            note = note.trim();
            userStory.put(getTime(), note);
            storage.put(chatRequest.username, userStory);
            return "### " + chatRequest.username + ", сохранено";
        }
    }

    private String getTime() {
        LocalDateTime now = LocalDateTime.now();
        long minutes = ChronoUnit.MINUTES.between(startTime, now);
        long hours = ChronoUnit.HOURS.between(startTime, now);
        long secs = ChronoUnit.SECONDS.between(startTime, now);
        return hours % 24 + ":" + minutes % 60 + ":" + secs % 60;
    }

    private String getHelpMessage() {
        return "Бот может сохранять заметки привязанные к таймингу подкаста,\n" +
                "доступно несколько команд\n" +
                "* sbot note/save {text} - сохранить заметку\n" +
                "* sbot list - показать список моих заметок\n" +
                "* sbot clear - очистить список заметок";
    }
}
