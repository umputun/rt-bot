/// <reference path="../typings/index.d.ts" />
import * as express from "express";
import {Express} from "express";
import * as bodyParser from "body-parser";
import {Request, Response} from "express-serve-static-core";
import {RequestData} from "./RequestData";
import {EventEmitter} from "events";
import {Bot} from "./Bot";


export class RESTServer extends EventEmitter {
    constructor(private bot: Bot) {
        super();

        var app: Express = express();
        app.use(bodyParser.json());
        app.get('/', this.defaultHandler.bind(this));
        app.get('/info', this.infoHandler.bind(this));
        app.post('/event', this.eventHandler.bind(this));
        app.listen(8080);
    }

    private defaultHandler(req: Request, res: Response) {
        res.send('anek-bot');
    }

    private infoHandler(req: Request, res: Response) {
        res.status(200);
        res.json(
            {
                info: 'anek-bot в ответ на фразу ' +
                '\'расскажи анекдот\' отвечает анекдотом ' +
                'полученным из RSS сайта anekdot.ru',
                author: 'Dmitry'
            }
        )
    }

    private eventHandler(req: Request, res: Response) {
        var requestData: RequestData = null;
        try {
            requestData = RequestData.parseFromObject(req.body);
        } catch (error) {
            res.status(400);
            res.json({error: error});
            return;
        }

        var answer = this.bot.getAnswer(requestData);
        if (answer == "no_answer") {
            res.status(417);
            res.end();
        } else {
            res.status(201);
            res.json({text: answer, bot: 'anek-bot'});
        }
    }
}