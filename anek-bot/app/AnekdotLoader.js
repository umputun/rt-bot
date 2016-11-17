"use strict";
var __extends = (this && this.__extends) || function (d, b) {
    for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p];
    function __() { this.constructor = d; }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
};
var request = require("request");
var xml2js = require('xml2js');
var AnekdotData_1 = require("./AnekdotData");
var events_1 = require("events");
var AnekdotLoader = (function (_super) {
    __extends(AnekdotLoader, _super);
    function AnekdotLoader() {
        _super.call(this);
    }
    AnekdotLoader.prototype.load = function (url) {
        var _this = this;
        //var url = "https://www.anekdot.ru/rss/tag/21.xml"; // Анекдоты про твиттер
        // var url = "https://www.anekdot.ru/rss/tag/26.xml"; // Анекдоты про программистов
        request({
            uri: url,
            method: 'GET',
            encoding: 'utf8'
        }, function (error, response, body) {
            if (error) {
                _super.prototype.emit.call(_this, 'error', error, url);
                return;
            }
            _this.parseXML(body, url);
        });
    };
    AnekdotLoader.prototype.parseXML = function (xmlString, url) {
        var _this = this;
        var anekdots = [];
        var parseString = xml2js.parseString;
        parseString(xmlString, function (error, result) {
            if (error) {
                _super.prototype.emit.call(_this, 'error', error, url);
                return;
            }
            var items = result.rss.channel[0].item;
            for (var _i = 0, items_1 = items; _i < items_1.length; _i++) {
                var item = items_1[_i];
                anekdots.push(AnekdotData_1.AnekdotData.parseFromObject(item));
            }
            _super.prototype.emit.call(_this, 'complete', url, anekdots);
        });
    };
    return AnekdotLoader;
}(events_1.EventEmitter));
exports.AnekdotLoader = AnekdotLoader;
