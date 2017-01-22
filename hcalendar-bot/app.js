//
// skeleton copy&pasted from https://github.com/umputun/rt-bot/tree/master/sovet-bot
//
const express = require('express');
const bodyParser = require('body-parser');
// const rp = require('request-promise');	// //,"request-promise": "^4.1.1"

var kdate = require("./kdate.js");
var formatting = require("./formatting.js")

var app = express(), port = 8080;

function getHebMonthOnEnglish(hMonth)
{
	var monthName = kdate.getHebMonth_v1(hMonth);
	return monthName;
}
function getHebMonth(hMonth)
{
	return getHebMonthOnEnglish(hMonth);
}

function hebDateToString(hebDate)
{
	var hmS = hebDate.substring(hebDate.indexOf(' ')+1, hebDate.length);
	var hDay = parseInt(hebDate.substring(0, hebDate.indexOf(' ')));
	var hMonth = parseInt(hmS.substring(0, hmS.indexOf(' ')))+1;
	var hYear = hmS.substring(hmS.indexOf(' ')+1, hmS.length);
	var hYearStr = hYear;

	var hebMonthName = getHebMonth(hMonth);
	var fullDate = formatting.FormatDay_v1(hDay) + " " + hebMonthName;
	fullDate = fullDate + ", " + hYearStr;
	return fullDate;
}

/*
{text: сообщение, username: id пользователя, display_name: имя пользователя} 
*/

app
.use(bodyParser.urlencoded({ extended: false }))
.use(bodyParser.json())

.get('/info', (req, res, next) => {
	res
	.status(200)
	.json({author: 'constructor-igor', info: 'Hebrew Calendar', commands: ['hcalendar']})
	.end();
})
.get('/event', (req, res, next) => {
	res
	.json({name: 'hcalendar bot', version: '0.0.1'})
	.end();
})
.post('/event', (req, res, next) => {
	var msg = req.body;

	if (msg.text == "hi hcalendar")
	{
		var data = {text: "hi", bot: "hcalendar-bot"};
		res
			.status(201)
			.json(data)
			.end();		
	} else
	if (msg.text == "hcalendar")
	{
		var uDate = new Date();
		var tday = uDate.getDate();
		var tmonth = uDate.getMonth() + 1;
		var tyear = uDate.getFullYear();

		var hebDate = kdate.civ2heb_v1(tday, tmonth, tyear);
		var currentData = hebDateToString(hebDate);
		var data = {text: currentData, bot: "hcalendar-bot"};
		res
			.status(201)
			.json(data)
			.end();
	} else{
		res.sendStatus(417);
	}
});

var server = app.listen(port);

server.on('error', function() {
  console.log("Error connection");
});