package com.m11;

import org.json.JSONObject;
import org.json.JSONString;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletResponse;

import java.lang.reflect.Array;

import static org.springframework.web.bind.annotation.RequestMethod.GET;
import static org.springframework.web.bind.annotation.RequestMethod.POST;

@RestController
public class RtbotController {

        @RequestMapping(value = "/info", method=GET, produces = "application/json; charset=utf-8")
        public String info () throws Exception {
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("author", "Mike Shemanskiy [@shamanskiy11](https://twitter.com/shamanskiy11)");
            jsonObject.put("info", "wiki-bot return first url form wiki search engine");
            jsonObject.put("commands", "['wiki java8', 'wiki rest']");
            return jsonObject.toString();
        }


    @RequestMapping(value = "/event", method=POST, produces = "application/json; charset=utf-8")
    public String event(@RequestBody Bot bot, HttpServletResponse rsp) throws Exception {

        WikiHandler wikiHandler = new WikiHandler();
        String wikiCheck = bot.getText().length() < 5 ? "" : bot.getText().substring(0,5);

        if (wikiCheck.trim().equals("wiki")){

            String request = bot.getText().replace("wiki", "").trim();

            if (request.isEmpty()){
                rsp.setStatus(HttpStatus.EXPECTATION_FAILED.value());
                return "";
            }

            String wikiUrl = wikiHandler.getWikiUrl(request);
            String result = wikiHandler.send(wikiUrl);

            if(!result.isEmpty()){

                rsp.setStatus(HttpStatus.CREATED.value());
                JSONObject jsonObject = new JSONObject();
                jsonObject.put("text", result);
                jsonObject.put("bot", "wiki-bot");
                return jsonObject.toString();
            } else {

                rsp.setStatus(HttpStatus.CREATED.value());
                JSONObject jsonObject = new JSONObject();
                jsonObject.put("text", "I don't know, ask Bobuk!");
                jsonObject.put("bot", "wiki-bot");
                return jsonObject.toString();
            }

        } else {
            rsp.setStatus(HttpStatus.EXPECTATION_FAILED.value());
            return "";
        }
    }
}
