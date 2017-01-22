"use strict";
var Bot = (function () {
    function Bot(channels) {
        this.channels = channels;
        this.defaultChannel = channels[0];
    }
    Bot.prototype.getAnswer = function (message) {
        if (!this.hasTriggerPhrase(message)) {
            return "no_answer";
        }
        var selectedChannel = this.defaultChannel;
        for (var _i = 0, _a = this.channels; _i < _a.length; _i++) {
            var channel = _a[_i];
            if (this.hasAnyWord(message, channel.getTags())) {
                selectedChannel = channel;
                break;
            }
        }
        return selectedChannel.getAnekdot().description;
    };
    Bot.prototype.hasTriggerPhrase = function (message) {
        var greyCommands = ["!грей", "грей!", "!gray", "gray!"];
        if (this.hasAnyWord(message, greyCommands)) {
            return true;
        }
        if (this.hasAllWords(message, ["расскаж", "анекдот"])) {
            return true;
        }
        return false;
    };
    Bot.prototype.hasAllWords = function (message, words) {
        var text = message.text.toLowerCase();
        for (var _i = 0, words_1 = words; _i < words_1.length; _i++) {
            var word = words_1[_i];
            if (text.indexOf(word) == -1) {
                return false;
            }
        }
        return true;
    };
    Bot.prototype.hasAnyWord = function (message, words) {
        var text = message.text.toLowerCase();
        for (var _i = 0, words_2 = words; _i < words_2.length; _i++) {
            var word = words_2[_i];
            if (text.indexOf(word) != -1) {
                return true;
            }
        }
        return false;
    };
    return Bot;
}());
exports.Bot = Bot;
