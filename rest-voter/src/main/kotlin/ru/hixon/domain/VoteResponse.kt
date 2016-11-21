package ru.hixon.domain

import com.fasterxml.jackson.annotation.JsonProperty

/**
 * Created by Denis on 17-Nov-16.
 */
data class VoteResponse(
        @JsonProperty("text")
        var text: String,

        @JsonProperty("bot")
        var botName: String = "rest-voter"
)