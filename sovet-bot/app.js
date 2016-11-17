const express = require('express');
const bodyParser = require('body-parser');
const rp = require('request-promise');

var app = express(), port = 8080;

/*
{text: сообщение, username: id пользователя, display_name: имя пользователя} 
*/

app
.use(bodyParser.urlencoded({ extended: false }))
.use(bodyParser.json())

.get('/event', (req, res, next) => {
	res
	.json({name: 'sovet bot', version: '0.0.1'})
	.end();
})
.post('/event', (req, res, next) => {
	var msg = req.body;

	if(/совет|грей|грэй|gray|как\sжить|подскажите|\?/i.test(msg.text)) {
		rp('http://fucking-great-advice.ru/api/random')
		.then(r => {
			var sovet = 'Совета нет(';
			try {
				r = JSON.parse(r);
				sovet = `##[Совет для: ${msg.username}] \`${r.text}\``;
			} catch(e) {};

			var data = {text: sovet, bot: "советчик"};

			res
			.status(201)
			.json(data)
			.end();

		})
		.catch(() => {
			res.sendStatus(417);
		});
	} else {
		 res.sendStatus(417);
	}

});

var server = app.listen(port);

server.on('error', function() {
  console.log("Error connection");
});