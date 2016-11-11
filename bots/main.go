// 2016, Egor Smolyakov (https://github.com/egorsmkv)
package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"strings"
	"time"
)

const botID = "bots"

type event struct {
	Text        string `json:"text"`
	Username    string `json:"username"`
	DisplayName string `json:"display_name"`
}

type response struct {
	Bot  string `json:"bot"`
	Text string `json:"text"`
}

func main() {
	log.Printf("bots bot")

	reportErr := func(err error, w http.ResponseWriter) {
		w.WriteHeader(http.StatusExpectationFailed)
		fmt.Fprintf(w, "%v", err)
	}

	handleCommand := func(command string) (string, error) {
		command = strings.ToLower(command)

		switch command {
		case "list":
			bots, err := botList()
			if err != nil {
				return "", err
			} else {
				return bots, nil
			}
		case "h", "help", "?":
			return "i have only one command - list", nil
		default:
			return "", errors.New("unknown command")
		}
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

		text, err := handleCommand(ev.Text)
		if err != nil {
			reportErr(err, w)
			return
		}

		resp := response{Bot: botID, Text: text}
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

func botList() (string, error) {
	resp, err := http.Get("https://bot.radio-t.com/list")
	if err != nil {
		resp.Body.Close()
		return "", err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	var bots []string
	err = json.Unmarshal(body, &bots)
	if err != nil {
		return "", err
	}

	if len(bots) == 0 {
		return "", errors.New("not found bots")
	}

	return strings.Join(bots, ", "), nil
}
