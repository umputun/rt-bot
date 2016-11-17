package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
)

type Source interface {
	Random() (string, error)
}

type DevelopersLife struct {
	Id            int16
	Description   string
	Votes         int16
	Author        string
	Date          string
	GifUrl        string
	PreviewUrl    string
	Type          string
	Width         string
	Height        string
	CommentsCount int16
	FileSize      int64
	CanVote       bool
}

func (s DevelopersLife) Random() (string, error) {

	err := s.GetItem(UrlRandomItem)
	if err != nil {
		return "", err
	}

	text := s.Description
	text = text + "  \n"
	text = text + fmt.Sprintf("![%v](%v)", s.Description, s.GifUrl)

	return text, nil
}

func (s *DevelopersLife) GetItem(url string) error {

	i := 0
	for {
		req, err := http.NewRequest("GET", url, nil)
		if err != nil {
			return err
		}

		client := &http.Client{}
		res, err := client.Do(req)
		if err != nil {
			return err
		}

		body, err := ioutil.ReadAll(res.Body)
		if err != nil {
			return err
		}

		err = json.Unmarshal(body, &s)
		if err != nil {
			return err
		}

		if s.isExistFile() {
			break
		}

		i++
		if i > MaxAttemps {
			return errors.New("Can't get gif image")
		}
	}

	return nil
}

func (s DevelopersLife) isExistFile() bool {

	if "" == s.GifUrl || "" == s.Description {
		return false
	}

	req, err := http.NewRequest("GET", s.GifUrl, nil)
	if err != nil {
		return false
	}

	client := &http.Client{}
	res, err := client.Do(req)
	if err != nil {
		return false
	}

	if 200 == res.StatusCode {
		return true
	}

	return false
}
