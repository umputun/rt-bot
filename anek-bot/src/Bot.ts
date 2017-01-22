import {RequestData} from "./RequestData";
import {AnekdotChannel} from "./AnekdotChannel";
export class Bot {

    private defaultChannel: AnekdotChannel;

    constructor(private channels: AnekdotChannel[]) {
        this.defaultChannel = channels[0];
    }

    public getAnswer(message: RequestData): string | "no_answer" {
        if (!this.hasTriggerPhrase(message)) {
            return "no_answer";
        }
        var selectedChannel = this.defaultChannel;
        for (var channel of this.channels) {
            if (this.hasAnyWord(message, channel.getTags())) {
                selectedChannel = channel;
                break;
            }
        }

        return selectedChannel.getAnekdot().description;
    }

    private hasTriggerPhrase(message: RequestData): boolean {

        var greyCommands = ["!грей", "грей!", "!gray", "gray!"];
        if (this.hasAnyWord(message, greyCommands)) {
            return true;
        }

        if (this.hasAllWords(message, ["расскаж", "анекдот"])) {
            return true;
        }

        return false;
    }

    private hasAllWords(message: RequestData, words: string[]): boolean {
        var text = message.text.toLowerCase();
        for (var word of words) {
            if (text.indexOf(word) == -1) {
                return false;
            }
        }

        return true;
    }

    private hasAnyWord(message: RequestData, words: string[]): boolean {
        var text = message.text.toLowerCase();
        for (var word of words) {
            if (text.indexOf(word) != -1) {
                return true;
            }
        }

        return false;
    }
}