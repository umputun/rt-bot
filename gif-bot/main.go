package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
)

type Info struct {
	Author   string   `json:"author"`
	Info     string   `json:"info"`
	Commands []string `json:"commands"`
}

func sendSuccess(w http.ResponseWriter, text []byte) {

	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusCreated)
	fmt.Fprintf(w, "%s", text)
}

func sendError(w http.ResponseWriter, err error) {

	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusExpectationFailed)
	fmt.Fprintf(w, "%v", err)
}

func info(w http.ResponseWriter, r *http.Request) {

	if r.Method != "GET" {
		return
	}

	info := Info{Author: BotAuthor, Info: BotDescription, Commands: BotCommands}
	text, err := json.Marshal(info)
	if err != nil {
		sendError(w, err)
		return
	}
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "%s", text)

	return
}

func handler(w http.ResponseWriter, r *http.Request) {

	if r.Method != "POST" {
		return
	}

	req := Request{}
	err := req.ParseData(r)
	if err != nil {
		sendError(w, err)
		return
	}

	command, err := req.ParseText()
	if err != nil {
		sendError(w, err)
		return
	}

	text := ""

	switch command {
	case "random":
		source := DevelopersLife{}
		text, err = source.Random()
		if err != nil {
			sendError(w, err)
		}
	default:
		sendError(w, errors.New("Uknown command"))
		return
	}

	resp := Response{Bot: BotId, Text: text}
	resTxt, err := resp.ToJson()
	if err != nil {
		sendError(w, err)
		return
	}

	sendSuccess(w, resTxt)
}

func panicRecover(f func(w http.ResponseWriter, r *http.Request)) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if r := recover(); r != nil {
				log.Printf("Pamic:%s\n", r)
			}
		}()
		f(w, r)
	}
}

func main() {

	http.HandleFunc("/info", panicRecover(info))
	http.HandleFunc("/event", panicRecover(handler))

	fmt.Printf("Start listening server on port %v", Port)
	log.Fatal(http.ListenAndServe(":"+Port, nil))
}
