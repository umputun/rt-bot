"use strict";
/// <reference path="../typings/index.d.ts" />
var RESTServer_1 = require("./RESTServer");
var AnekdotLoader_1 = require("./AnekdotLoader");
var AnekdotChannel_1 = require("./AnekdotChannel");
var Bot_1 = require("./Bot");
console.log("Anek-bot starting");
var loader = new AnekdotLoader_1.AnekdotLoader();
var channels = [];
channels.push(new AnekdotChannel_1.AnekdotChannel(loader, "https://www.anekdot.ru/rss/tag/26.xml", []));
channels.push(new AnekdotChannel_1.AnekdotChannel(loader, "https://www.anekdot.ru/rss/tag/21.xml", ["твиттер", "twitter"]));
channels.push(new AnekdotChannel_1.AnekdotChannel(loader, "https://www.anekdot.ru/rss/tag/33.xml", ["гейтс"]));
channels.push(new AnekdotChannel_1.AnekdotChannel(loader, "https://www.anekdot.ru/rss/tag/37.xml", ["интернет"]));
channels.push(new AnekdotChannel_1.AnekdotChannel(loader, "https://www.anekdot.ru/rss/tag/40.xml", ["apple", "эппл", "iphone", "айфон", "ipad"]));
var bot = new Bot_1.Bot(channels);
var server = new RESTServer_1.RESTServer(bot);
