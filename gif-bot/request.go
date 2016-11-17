package main

import (
	"encoding/json"
	"errors"
	"io/ioutil"
	"log"
	"net/http"
	"strings"
	"time"
)

type Request struct {
	Text        string `json:"text"`
	Username    string `json:"username"`
	DisplayName string `json:"display_name"`
}

func (req *Request) ParseData(r *http.Request) error {

	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		return err
	}

	err = json.Unmarshal(body, &req)
	if err != nil {
		return err
	}

	req.LogRequest(r)
	return nil
}

func (req *Request) ParseText() (string, error) {

	if "" == req.Text {
		return "", errors.New("Empty request text")
	}

	if strings.HasPrefix(strings.ToLower(req.Text), "показать гифку") {
		return "random", nil
	}

	return "", errors.New("Unknown command")
}

func (req *Request) LogRequest(r *http.Request) {

	st := time.Now()
	log.Printf("%+v - %v - %s - %s", req.Username, time.Since(st), r.RemoteAddr, r.UserAgent())
}
