package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"time"
)

const botID = "brackets-bot"

type event struct {
	Text        string `json:"text"`
	Username    string `json:"username"`
	DisplayName string `json:"display_name"`
}

type response struct {
	Text string `json:"text"`
	Bot  string `json:"bot"`
}

func main() {
	log.Printf("brackets-bot")

	reportErr := func(err error, w http.ResponseWriter) {
		w.WriteHeader(http.StatusExpectationFailed)
		fmt.Fprintf(w, "%v", err)
	}

	http.HandleFunc("/event", func(w http.ResponseWriter, r *http.Request) {

		st := time.Now()
		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
			reportErr(err, w)
			return
		}

		ev := event{}
		if err = json.Unmarshal(body, &ev); err != nil {
			reportErr(err, w)
			return
		}

		text_resp, err := processString(ev.Text)
		if err != nil {
			reportErr(err, w)
			return
		}
		if text_resp == "" {
			reportErr(errors.New("Empty result"), w)
			return
		}

		resp := response{
			Bot:  botID,
			Text: fmt.Sprintf("%s\nЗакрывай скобки, @%s !!!", text_resp, ev.Username),
		}
		bresp, err := json.Marshal(resp)
		if err != nil {
			reportErr(err, w)
			return
		}

		log.Printf("%+v - %v - %s - %s", ev, time.Since(st), r.RemoteAddr, r.UserAgent())
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(http.StatusCreated)
		fmt.Fprintf(w, "%s", string(bresp))
	})

	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatalf("failed to start server, %v", err)
	}
}
