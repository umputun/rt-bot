/// <reference path="../typings/index.d.ts" />
import {RESTServer} from "./RESTServer";
import {AnekdotLoader} from "./AnekdotLoader";
import {AnekdotChannel} from "./AnekdotChannel";
import {Bot} from "./Bot";

console.log("Anek-bot starting");

var loader = new AnekdotLoader();
var channels: AnekdotChannel[] = [];
channels.push(new AnekdotChannel(loader, "https://www.anekdot.ru/rss/tag/26.xml", []));
channels.push(new AnekdotChannel(loader, "https://www.anekdot.ru/rss/tag/21.xml", ["твиттер", "twitter"]));
channels.push(new AnekdotChannel(loader, "https://www.anekdot.ru/rss/tag/33.xml", ["гейтс"]));
channels.push(new AnekdotChannel(loader, "https://www.anekdot.ru/rss/tag/37.xml", ["интернет"]));
channels.push(new AnekdotChannel(loader, "https://www.anekdot.ru/rss/tag/40.xml", ["apple", "эппл", "iphone", "айфон", "ipad"]));

var bot = new Bot(channels);

var server = new RESTServer(bot);