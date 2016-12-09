let express = require('express');
let bodyParser = require('body-parser');
let request = require('request');
let app = express();
app.use(bodyParser.urlencoded({
    extended: true
}));
app.use(bodyParser.json());
const currency = {
    d: /([0-9]+\s?|[0-9]+(,|\.)[0-9]+\s?)(?=\$|дол|доларов|dolarow|dolar|dol)/i,
    e: /([0-9]+\s?|[0-9]+(,|\.)[0-9]+\s?)(?=€|евро|эвро|euro|ewro)/i,
    h: /([0-9]+\s?|[0-9]+(,|\.)[0-9]+\s?)(?=₴|грн|гривень|гривны|hrn|hriven)/i,
    r: /([0-9]+\s?|[0-9]+(,|\.)[0-9]+\s?)(?=₽|рублей|рубли|рубль|руб|rub|rublej|rublei)/i
};


app.post('/event', function(req, res) {
    let text = req.body.text;
    let v = 0;
    let c = 0;
    if(text.match(currency.d)!=null){
        v = text.match(currency.d)[0];
        c = "USD";
    }
    else if(text.match(currency.e)!=null){
        v = text.match(currency.e)[0];
        c = "EUR";
    }
    else if(text.match(currency.h)!=null){
        v = text.match(currency.h)[0];
        c = "UAH";
    }
    else if(text.match(currency.r)!=null){
        v = text.match(currency.r)[0];
        c = "RUB";
    }
    if(v!=0 && c!=0){
        request("http://free.currencyconverterapi.com/api/v3/convert?q="+c+"_USD,"+c+"_EUR,"+c+"_UAH,"+c+"_RUB", function (error, response, body) {
            if (!error && response.statusCode == 200) {
                let results = JSON.parse(body).results;
                let quotes = Object.keys(results).map(function (key) { return results[key]; });
                let inDolar = (quotes[0].val*parseFloat(v)).toFixed(2);
                let inEuro = (quotes[1].val*parseFloat(v)).toFixed(2);
                let inHrn = (quotes[2].val*parseFloat(v)).toFixed(2);
                let inRub = (quotes[3].val*parseFloat(v)).toFixed(2);

                let responseText = "";
                if(c!="USD") responseText += inDolar + " USD\n";
                if(c!="EUR") responseText += inEuro + " EUR\n";
                if(c!="UAH") responseText += inHrn + " UAH\n";
                if(c!="RUB") responseText += inRub + " RUB\n";

                res.status(201);
                res.json({
                    bot: "money_bot",
                    text: responseText
                });
                res.end();
            }
            else res.status(417).end();
        });
    }
    else res.status(417).end();
});

app.all('/info', function(req, res) {
    res.json({
        author: 'exelban',
        info: 'Если в сообщение была упомянутая какая то валюта то конвертирует ее в долар, евро, грн, руб. (30$ = 27.95 EUR, 1,9101.85 руб...)'
    });
    res.end();
});


app.listen(8080);
