package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"regexp"
	"time"
)

const botID = "excerpt"

type event struct {
	Text        string `json:"text"`
	Username    string `json:"username"`
	DisplayName string `json:"display_name"`
}

type response struct {
	Text string `json:"text"`
	Bot  string `json:"bot"`
}

var rLink = regexp.MustCompile(`(https?\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?)`)
var rImg = regexp.MustCompile(`\.gif|\.jpg|\.jpeg|\.png`)

func main() {
	log.Printf("excerpt bot")

	answer := func(s string) (string, error) {
		link, err := link(s)
		if err == nil {
			return excerpt(link)
		}
		return "", err
	}

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

		ex, err := answer(ev.Text)
		if err != nil {
			reportErr(err, w)
			return
		}
		resp := response{Bot: botID, Text: ex}
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

	http.HandleFunc("/info", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(`{"author": "umputun", "info": "excerpt бот раскрывает ссылки в короткое описание"}`))
	})

	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatalf("failed to start server, %v", err)
	}
}

func excerpt(link string) (result string, err error) {
	client := http.Client{Timeout: 5 * time.Second}
	url := "http://parser.ukeeper.com/api/content/v1/parser?token=not-in-use-yet&url=" + link
	resp, err := client.Get(url)
	if err != nil {
		return "", err
	}
	defer func() { _ = resp.Body.Close() }()

	if resp.StatusCode >= 400 {
		return "", errors.New(resp.Status)
	}

	response := struct {
		// Content   string `json:"content"`
		// Rich      string `json:"rich_content"`
		// Domain    string `json:"domain"`
		// Author    string `json:"author"`
		// URL       string `json:"url"`
		Title   string `json:"title"`
		Excerpt string `json:"excerpt"`
		// Published string `json:"date_published"`
		// Dek       string `json:"dek"`
		// Image     string `json:"lead_image_url"`
	}{}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	if err := json.Unmarshal(body, &response); err != nil {
		return "", err
	}

	return fmt.Sprintf("%s\\n\\n_%s_", response.Excerpt, response.Title), nil
}

func link(input string) (link string, err error) {
	if link := rLink.FindString(input); link != "" && !rImg.MatchString(link) {
		log.Printf("found a link %s", link)
		return link, nil
	}
	return "", errors.New("no link found")
}
