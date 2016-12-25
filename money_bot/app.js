let express = require('express');
let bodyParser = require('body-parser');
let request = require('request');
let waterfall = require('async/waterfall');
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
    waterfall([
        function(callback){
            let v = 0;
            let c = 0;
            if(text.match(currency.d)!=null){
                v = text.match(currency.d)[0];
                c = "USD";
                callback(null, v, c);
            }
            else if(text.match(currency.e)!=null){
                v = text.match(currency.e)[0];
                c = "EUR";
                callback(null, v, c);
            }
            else if(text.match(currency.h)!=null){
                v = text.match(currency.h)[0];
                c = "UAH";
                callback(null, v, c);
            }
            else if(text.match(currency.r)!=null){
                v = text.match(currency.r)[0];
                c = "RUB";
                callback(null, v, c);
            }
            else callback(true);
        },
        function(v, c, callback){
            if(~v.indexOf("сотень")) v = v.replace("сотень", "00");
            if(~v.indexOf("сотни")) v = v.replace("сотни", "00");
            if(~v.indexOf("тысяч")) v = v.replace("тысяч", "000");
            if(~v.indexOf("тысячи")) v = v.replace("тысячи", "000");
            if(~v.indexOf("милион")) v = v.replace("милион", "000000");
            if(~v.indexOf("милионов")) v = v.replace("милионов", "000000");
            v = v.replace(/[^\d(,|\.)-]/g, '');
            callback(null, v, c);
        },
        function(v, c, callback){
            request("http://free.currencyconverterapi.com/api/v3/convert?q="+c+"_USD,"+c+"_EUR,"+c+"_UAH,"+c+"_RUB", function (error, response, body) {
                if (!error && response.statusCode == 200) {
                    let results = JSON.parse(body).results;
                    let quotes = Object.keys(results).map(function (key) { return results[key]; });
                    let inDolar = (quotes[0].val*parseFloat(v)).toFixed(2);
                    let inEuro = (quotes[1].val*parseFloat(v)).toFixed(2);
                    let inHrn = (quotes[2].val*parseFloat(v)).toFixed(2);
                    let inRub = (quotes[3].val*parseFloat(v)).toFixed(2);
                    
                    let responseParts = [];
                    if(c!="USD") responseParts.push((inDolar.replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ') + " $").replace(".00", ""));
                    if(c!="EUR") responseParts.push((inEuro.replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ') + " €").replace(".00", ""));
                    if(c!="UAH") responseParts.push((inHrn.replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ') + " грн.").replace(".00", ""));
                    if(c!="RUB") responseParts.push((inRub.replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ') + " руб.").replace(".00", ""));
                    let responseText = responseParts.join(" | ");

                    callback(null, responseText);
                }
                else callback(true);
            });
        }
    ], function (err, result) {
        if(err) res.status(417).end();
        else {
            res.status(201);
            res.json({
                bot: "money_bot",
                text: result
            });
            res.end();
        }
    });
});
app.all('/info', function(req, res) {
    res.json({
        author: 'exelban',
        info: 'Если в сообщение была упомянутая какая-то валюта (USD, EUR, UAH, RUB), бот конвертирует ее в доллары, евро, грн, руб. (5€ = 5.30 $ | 136.67 грн. | 335.51 руб.)'
    });
    res.end();
});

app.listen(8080);
