"use strict";
const express           = require('express');
const bodyParser        = require('body-parser');
const request           = require('request');
const waterfall         = require('async/waterfall');
const mongoose          = require('mongoose');
let app = express();
app.use(bodyParser.urlencoded({
    extended: true
}));
app.use(bodyParser.json());
mongoose.Promise = global.Promise;
mongoose.connect("mongodb://stone_bot_db/stone_bot", function(err) {
    if (err) throw err;
});

const userModel = new mongoose.Schema({
    from: { type: String, required: true },
    date: { type: String, required: true }
});
const regex = {
    c1: /^(\/stone\s|бросить камень|throw a stone)/i,
    c2: /^\/stones\s/i
};
const res1 = "___ кинул в --- камень.";
const res2 = "Вы можете кинуть камень в того самого пользователя только 3 раза за 24 часа.";
const res3 = "Вы не можете кинуть камень в самого себя.";
const res4 = "В пользователя ___ кинули камень --- раз.";


app.post('/event', function(req, res) {
    let text = req.body.text;
    let userName = req.body.username;
    let display_name = req.body.display_name;
    waterfall([
        function(callback){
            if(text.match(regex.c1)!=null) callback(null, text.split("@")[1], 1);
            else if(text.match(regex.c2)!=null) callback(null, text.split("@")[1], 2);
            else callback(true);
        },
        function (name, action, callback) {
            let userDB = mongoose.model('user_'+name, userModel);
            if(action==1){
                if(name==userName.replace("@", "")) callback(null, res3);
                else{
                    userDB.find({from: userName, $where:"new Date(new Date(this.date).getTime() + 24 * 60 * 60 * 1000)<new Date()"}, function (err, stones) {
                        if(stones.length < 3){
                            let throwStone = new userDB({
                                from: userName,
                                date: new Date().toJSON()
                            });
                            throwStone.save(function (err) {
                                if (!err) callback(null, res1.replace("___", display_name).replace("---", "@"+name));
                                else callback(true);
                            });
                        }
                        else if(stones.length >= 3) callback(null, res2);
                    });
                }
            }
            else if(action==2){
                userDB.find(function (err, stones) {
                    callback(null, res4.replace("___", "@"+name).replace("---", stones.length));
                });
            }
        }],
        function (err, result) {
            if(err) res.status(417).end();
            else {
                res.status(201);
                res.json({
                    bot: "stone_bot",
                    text: result
                });
                res.end();
            }
        }
    );
});
app.all('/info', function(req, res) {
    res.json({
        author: 'exelban',
        info: 'Бот который помагает бросить камень в пользователя)'
    });
    res.end();
});


app.listen(8080);
