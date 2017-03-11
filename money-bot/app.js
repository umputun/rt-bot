"use strict";
const   express         = require('express'),
        bodyParser      = require('body-parser'),
        request         = require('request'),
        waterfall       = require('async/waterfall'),
        cron            = require('node-cron'),
        fs              = require('fs');
const app = express();
app.use(bodyParser.urlencoded({
    extended: true
}));
app.use(bodyParser.json());
const currency_RegExp = {
    d: /(((\$|usd)\s?)(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?)|(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?(\s(милион|тысяч|сотень|сотни|k|к)\s?)?(\s?(\$|дол|dol|баксов|usd))))/i,
    e: /(((€|eur)\s?)(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?)|(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?(\s(милион|тысяч|сотень|сотни|k|к)\s?)?(\s?(€|евро|эвро|eur|ewro))))/i,
    h: /(((₴|uah)\s?)(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?)|(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?(\s(милион|тысяч|сотень|сотни|k|к)\s?)?(\s?(₴|грн|гривень|гривны|hrn|hriven|uah))))/i,
    r: /(((₽|rub)\s?)(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?)|(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?(\s(милион|тысяч|сотень|сотни|k|к)\s?)?(\s?(₽|руб|rub))))/i,
    b: /(((Br|BYN)\s?)(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?)|(([0-9]+\s[0-9]+\s[0-9]+|[0-9]+\s[0-9]+|[0-9]+)((,|\.)[0-9]+)?(\s(милион|тысяч|сотень|сотни|k|к)\s?)?(\s?(Br|белорусских рублей|белорусских|BYN))))/i
};
let currency = {
    USD_EUR: 0,
    USD_UAH: 0,
    USD_RUB: 0,
    USD_BYN: 0,
    EUR_USD: 0,
    EUR_UAH: 0,
    EUR_RUB: 0,
    EUR_BYN: 0,
    UAH_USD: 0,
    UAH_EUR: 0,
    UAH_RUB: 0,
    UAH_BYN: 0,
    RUB_USD: 0,
    RUB_EUR: 0,
    RUB_UAH: 0,
    RUB_BYN: 0,
    BYN_USD: 0,
    BYN_EUR: 0,
    BYN_UAH: 0,
    BYN_RUB: 0
};


app.post('/event', function(req, res) {
    let text = req.body.text;
    waterfall([
        function(callback){
            let v = 0;
            let c = 0;
            if(text.match(currency_RegExp.d)!=null){
                v = text.match(currency_RegExp.d)[0];
                c = "USD";
                callback(null, v, c);
            }
            else if(text.match(currency_RegExp.e)!=null){
                v = text.match(currency_RegExp.e)[0];
                c = "EUR";
                callback(null, v, c);
            }
            else if(text.match(currency_RegExp.h)!=null){
                v = text.match(currency_RegExp.h)[0];
                c = "UAH";
                callback(null, v, c);
            }
            else if(text.match(currency_RegExp.r)!=null){
                v = text.match(currency_RegExp.r)[0];
                c = "RUB";
                callback(null, v, c);
            }
            else if(text.match(currency_RegExp.b)!=null){
                v = text.match(currency_RegExp.b)[0];
                c = "BYN";
                callback(null, v, c);
            }
            else callback(true);
        },
        function(v, c, callback){
            let res_1 = 0,
                res_2 = 0,
                res_3 = 0,
                res_4 = 0,
                cur_1 = 0,
                cur_2 = 0,
                cur_3 = 0,
                cur_4 = 0,
                name_1 = 0,
                name_2 = 0,
                name_3 = 0,
                name_4 = 0;

            if(c=="USD"){
                res_1 = ((currency.USD_EUR*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_2 = ((currency.USD_UAH*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_3 = ((currency.USD_RUB*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_4 = ((currency.USD_BYN*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                cur_1 = currency.USD_EUR;
                cur_2 = currency.USD_UAH;
                cur_3 = currency.USD_RUB;
                cur_4 = currency.USD_BYN;
                name_1 = "EUR";
                name_2 = "UAH";
                name_3 = "RUB";
                name_4 = "BYN";
            }
            else if(c=="EUR"){
                res_1 = ((currency.EUR_USD*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_2 = ((currency.EUR_UAH*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_3 = ((currency.EUR_RUB*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_4 = ((currency.EUR_BYN*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                cur_1 = currency.EUR_USD;
                cur_2 = currency.EUR_UAH;
                cur_3 = currency.EUR_RUB;
                cur_4 = currency.EUR_BYN;
                name_1 = "USD";
                name_2 = "UAH";
                name_3 = "RUB";
                name_4 = "BYN";
            }
            else if(c=="UAH"){
                res_1 = ((currency.UAH_USD*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_2 = ((currency.UAH_EUR*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_3 = ((currency.UAH_RUB*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_4 = ((currency.UAH_BYN*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                cur_1 = currency.UAH_USD;
                cur_2 = currency.UAH_EUR;
                cur_3 = currency.UAH_RUB;
                cur_4 = currency.UAH_BYN;
                name_1 = "USD";
                name_2 = "EUR";
                name_3 = "RUB";
                name_4 = "BYN";
            }
            else if(c=="RUB"){
                res_1 = ((currency.RUB_USD*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_2 = ((currency.RUB_EUR*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_3 = ((currency.RUB_UAH*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_4 = ((currency.RUB_BYN*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                cur_1 = currency.RUB_USD;
                cur_2 = currency.RUB_EUR;
                cur_3 = currency.RUB_UAH;
                cur_4 = currency.RUB_BYN;
                name_1 = "USD";
                name_2 = "EUR";
                name_3 = "UAH";
                name_4 = "BYN";
            }
            else if(c=="BYN"){
                res_1 = ((currency.BYN_USD*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_2 = ((currency.BYN_EUR*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_3 = ((currency.BYN_UAH*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                res_4 = ((currency.BYN_RUB*parseFloat(v)).toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')).replace(".00", "");
                cur_1 = currency.BYN_USD;
                cur_2 = currency.BYN_EUR;
                cur_3 = currency.BYN_UAH;
                cur_4 = currency.BYN_RUB;
                name_1 = "USD";
                name_2 = "EUR";
                name_3 = "UAH";
                name_4 = "RUB";
            }

            let responseText = "**_"+req.body.username+"_** упомянул " + v + " "+ c + "\\n\\n"+
                "| "+c+"           | "+v+"           | Курсы           | \\n"+
                "|:-------------:|:--------------:|:--------------:|\\n"+
                "| "+name_1+" | "+res_1+" | "+cur_1.toFixed(2)+" |\\n"+
                "| "+name_2+" | "+res_2+" | "+cur_2.toFixed(2)+" |\\n"+
                "| "+name_3+" | "+res_3+" | "+cur_3.toFixed(2)+" |\\n"+
                "| "+name_4+" | "+res_4+" | "+cur_4.toFixed(2)+" |";

            callback(null, responseText);
        }
    ], function (err, result) {
        if(err) res.status(417).end();
        else {
            res.status(201);
            res.json({
                bot: "money-bot",
                text: result
            });
            res.end();
        }
    });
});
app.all('/info', function(req, res) {
    res.json({
        author: 'exelban',
        info: 'Если в сообщение была упомянутая какая-то валюта (USD, EUR, UAH, RUB), бот конвертирует ее в доллары, евро, грн, руб.'
    });
    res.end();
});


function get_currency(){
    waterfall([
        function(callback){
            request("http://free.currencyconverterapi.com/api/v3/convert?q=USD_EUR,USD_UAH,USD_RUB,USD_BYN,EUR_USD,EUR_UAH,EUR_RUB,EUR_BYN,UAH_USD", {timeout: 3000}, function (error, response, body) {
                if (!error && response.statusCode == 200) {
                    let results = JSON.parse(body).results;
                    let quotes = Object.keys(results).map(function (key) { return results[key]; });
                    currency.USD_EUR = quotes[0].val;
                    currency.USD_UAH = quotes[1].val;
                    currency.USD_RUB = quotes[2].val;
                    currency.USD_BYN = quotes[3].val;
                    currency.EUR_USD = quotes[4].val;
                    currency.EUR_UAH = quotes[5].val;
                    currency.EUR_RUB = quotes[6].val;
                    currency.EUR_BYN = quotes[7].val;
                    currency.UAH_USD = quotes[8].val;
                    callback(null);
                }
                else {
                    callback(true);
                }
            });
        },
        function(callback){
            request("http://free.currencyconverterapi.com/api/v3/convert?q=UAH_EUR,UAH_RUB,UAH_BYN,RUB_USD,RUB_EUR,RUB_UAH,RUB_BYN,BYN_USD,BYN_EUR,BYN_UAH", {timeout: 3000}, function (error, response, body) {
                if (!error && response.statusCode == 200) {
                    let results = JSON.parse(body).results;
                    let quotes = Object.keys(results).map(function (key) { return results[key]; });
                    currency.UAH_EUR = quotes[0].val;
                    currency.UAH_RUB = quotes[1].val;
                    currency.UAH_BYN = quotes[2].val;
                    currency.RUB_USD = quotes[3].val;
                    currency.RUB_EUR = quotes[4].val;
                    currency.RUB_UAH = quotes[5].val;
                    currency.RUB_BYN = quotes[6].val;
                    currency.BYN_USD = quotes[7].val;
                    currency.BYN_EUR = quotes[8].val;
                    currency.BYN_UAH = quotes[9].val;
                    callback(null);
                }
                else callback(true);
            });
        },
        function(callback){
            request("http://free.currencyconverterapi.com/api/v3/convert?q=BYN_RUB", {timeout: 3000}, function (error, response, body) {
                if (!error && response.statusCode == 200) {
                    let results = JSON.parse(body).results;
                    let quotes = Object.keys(results).map(function (key) { return results[key]; });
                    currency.BYN_RUB = quotes[0].val;
                    callback(null);
                }
                else callback(true);
            });
        }
    ], function (err) {
        if(err) {
            fs.readFile('currency.json', 'utf8', function (err, data) {
                if (err) throw err;
                currency = JSON.parse(data);
            });
        }
        else fs.writeFileSync("currency.json", JSON.stringify(currency));
    });
}


cron.schedule('56 * * * *', get_currency());
get_currency();
app.listen(8080);
