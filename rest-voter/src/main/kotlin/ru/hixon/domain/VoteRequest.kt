package ru.hixon.domain

import com.fasterxml.jackson.annotation.JsonProperty


/**
 * Created by Denis on 17-Nov-16.
 */
data class VoteRequest(
        @JsonProperty("text")
        var textCommand: String,

        @JsonProperty("username")
        var userName: String,

        @JsonProperty("display_name")
        var displayName: String
)