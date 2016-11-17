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
    //TODO refactor to hasAllWords
    Bot.prototype.hasTriggerPhrase = function (message) {
        var text = message.text.toLowerCase();
        if (text.indexOf('расскажи') != -1 && text.indexOf('анекдот') != -1) {
            return true;
        }
        return false;
    };
    Bot.prototype.hasAnyWord = function (message, words) {
        var text = message.text.toLowerCase();
        for (var _i = 0, words_1 = words; _i < words_1.length; _i++) {
            var word = words_1[_i];
            if (text.indexOf(word) != -1) {
                return true;
            }
        }
        return false;
    };
    return Bot;
}());
exports.Bot = Bot;
