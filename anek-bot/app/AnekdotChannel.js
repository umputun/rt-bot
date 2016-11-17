"use strict";
var AnekdotData_1 = require("./AnekdotData");
var AnekdotChannel = (function () {
    function AnekdotChannel(loader, rssUrl, tags) {
        this.loader = loader;
        this.tags = [];
        this.anekdots = [AnekdotData_1.AnekdotData.getDefaultAnekdot()];
        this.index = 0;
        this.load(rssUrl, tags);
    }
    AnekdotChannel.prototype.getTags = function () {
        return this.tags;
    };
    AnekdotChannel.prototype.getAnekdot = function () {
        if (this.index >= this.anekdots.length) {
            this.index = 0;
        }
        var anekdot = this.anekdots[this.index];
        this.index++;
        return anekdot;
    };
    AnekdotChannel.prototype.load = function (rssUrl, tags) {
        this.rssUrl = rssUrl;
        this.tags = tags;
        this.loader.on('error', this.onLoadError.bind(this));
        this.loader.on('complete', this.onLoadComplete.bind(this));
        this.loader.load(rssUrl);
    };
    AnekdotChannel.prototype.onLoadError = function (error, url) {
        console.log("Error while loading " + url + ". Details: " + error);
    };
    AnekdotChannel.prototype.onLoadComplete = function (url, anekdots) {
        if (url != this.rssUrl) {
            return;
        }
        console.log("Anekdots loaded. URL: " + url + " Tags: " + this.tags);
        this.anekdots = anekdots;
        this.index = 0;
    };
    return AnekdotChannel;
}());
exports.AnekdotChannel = AnekdotChannel;
