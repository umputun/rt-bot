package ru.hixon.domain

import com.fasterxml.jackson.annotation.JsonProperty

/**
 * Created by Denis on 18-Nov-16.
 */
data class InfoResponse(
        @JsonProperty("author")
        var author: String = "http://hixon.ru",

        @JsonProperty("info")
        var info: String = "Бот для создания голосований.",

        @JsonProperty("commands")
        var commands: List<String>
)