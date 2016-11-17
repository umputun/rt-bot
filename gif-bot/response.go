package main

import (
	"encoding/json"
)

type Response struct {
	Text string `json:"text"`
	Bot  string `json:"bot"`
}

func (r *Response) ToJson() ([]byte, error) {

	text, err := json.Marshal(r)
	if err != nil {
		return nil, err
	}
	return text, nil
}
