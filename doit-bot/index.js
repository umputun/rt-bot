const express = require('express');
const bodyParser = require('body-parser');
const triggers = require('./triggers.json');
const app = express();

const getTrigger = (message) =>
	triggers.filter(t => new RegExp(`${t.w}$`, 'i').test(message.trim()))[0];

const getIndex = (arr) =>
	Math.floor(Math.random() * (arr.length - 0));
	
const getAnswer = ({a}) => a[getIndex(a)];

const getResult = (trigger, username) => ({
	text: `@${username} ${getAnswer(trigger)}`,
	bot: 'doit-bot'
});

const info = ({
	author: 'Ildar Gilfanov @rabinzon',
	info: 'Бот побуждает на разного рода действия, вбрасывая цитаты из [ Shia Labeouf "Just do it"](https://goo.gl/eD9hRr)'
});

app.use(bodyParser.json());

const nothingToSay = res => res.status(417).end();

app.post('/event', (req, res) => {
	const {text, username} = req.body;
	
	if (typeof text !== 'string') return nothingToSay(res);
	
	const trigger = getTrigger(text);

	if (trigger) {
		res.status(201);
		res.json(getResult(trigger, username));
	}
	else nothingToSay(res);
});

app.all('/info', (req, res) => res.json(info));

app.all('/', (req, res) => res.json(info));

app.listen(8080);
