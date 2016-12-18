let express = require('express');
let bodyParser = require('body-parser');
let request = require('request');
let app = express();
app.use(bodyParser.urlencoded({
    extended: true
}));
app.use(bodyParser.json());
const currency = {
    d: /(((\$|usd)\s?)(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?)|(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?(\s(милион|тысяч|сотень|сотни)\s?)?(\s?(\$|дол|dol|баксов|usd))))/i,
    e: /(((€|eur)\s?)(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?)|(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?(\s(милион|тысяч|сотень|сотни)\s?)?(\s?(€|евро|эвро|eur|ewro))))/i,
    h: /(((₴|uah)\s?)(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?)|(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?(\s(милион|тысяч|сотень|сотни)\s?)?(\s?(₴|грн|гривень|гривны|hrn|hriven|uah))))/i,
    r: /(((₽|rub)\s?)(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?)|(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?(\s(милион|тысяч|сотень|сотни)\s?)?(\s?(₽|руб|rub))))/i
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
        if(~v.indexOf("сотень")) v = v.replace("сотень", "00");
        if(~v.indexOf("сотни")) v = v.replace("сотни", "00");
        if(~v.indexOf("тысяч")) v = v.replace("тысяч", "000");
        if(~v.indexOf("тысячи")) v = v.replace("тысячи", "000");
        if(~v.indexOf("милион")) v = v.replace("милион", "000000");
        if(~v.indexOf("милионов")) v = v.replace("милионов", "000000");
        v = v.replace(/[^\d(,|\.)-]/g, '');
        request("http://free.currencyconverterapi.com/api/v3/convert?q="+c+"_USD,"+c+"_EUR,"+c+"_UAH,"+c+"_RUB", function (error, response, body) {
            if (!error && response.statusCode == 200) {
                let results = JSON.parse(body).results;
                let quotes = Object.keys(results).map(function (key) { return results[key]; });
                let inDolar = (quotes[0].val*parseFloat(v)).toFixed(2);
                let inEuro = (quotes[1].val*parseFloat(v)).toFixed(2);
                let inHrn = (quotes[2].val*parseFloat(v)).toFixed(2);
                let inRub = (quotes[3].val*parseFloat(v)).toFixed(2);

                let responseParts = [];
                if(c!="USD") responseParts.push(inDolar.replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ') + " USD");
                if(c!="EUR") responseParts.push(inEuro.replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ') + " EUR");
                if(c!="UAH") responseParts.push(inHrn.replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ') + " UAH");
                if(c!="RUB") responseParts.push(inRub.replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ') + " RUB");
                let responseText = responseParts.join(" - ");

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
        info: 'Если в сообщение была упомянутая какая-то валюта (USD, EUR, UAH, RUB), бот конвертирует ее в доллары, евро, грн, руб. (5€ = 5.30 USD, 136.67 UAH, 335.51 RUB)'
    });
    res.end();
});


app.listen(8080);
