package main

import "testing"

func TestBracketsGood(t *testing.T) {
	cases := []struct {
		in, want string
	}{
		{"(", ")"},
		{"", ""},
		{"((()", "))"},
		{"(([", "]))"},
		{"()()()([{", "}])"},
	}
	for _, c := range cases {
		result, err := processString(c.in)
		if err != nil {
			t.Errorf("Input: '%s'. Error: '%s", c.in, err.Error())
		}
		if result != c.want {
			t.Errorf("Input: '%s'. Wanted: '%s'. Got: '%s'", c.in, c.want, result)
		}
	}
}

func TestBracketsBad(t *testing.T) {
	cases := []struct {
		in  string
		err error
	}{
		{"(]", inconsistentError},
		{"(({]", inconsistentError},
	}
	for _, c := range cases {
		_, err := processString(c.in)
		if err != c.err {
			t.Errorf("Input: '%s'. Wanted: '%s'. Got: '%s'", c.in, err.Error(), c.err.Error())
		}
	}
}
