package main

import (
	"testing"
	"regexp"
)

func TestGetRandom(t *testing.T) {
	result := GetRandom("Да Нет")
	match, _ := regexp.MatchString("^((Да)|(Нет))", result)
	if !match {
		t.Error("should return random value")
	}
}
