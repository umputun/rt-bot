package main

import "testing"

func TestLink(t *testing.T) {

	tbl := []struct {
		inp  string
		link string
		err  bool
	}{
		{"blah", "", true},
		{"blah http://radio-t.com blah2", "http://radio-t.com", false},
		{"https://radio-t.com blah2", "https://radio-t.com", false},
		{"blah http://radio-t.com/aa.gif blah2", "", true},
		{"blah https://radio-t.com/aa.png blah2", "", true},
		{"blah https://radio-t.com/png blah2", "https://radio-t.com/png", false},
		{"blah https://twitter.com/radio_t/status/811670832510537730", "", true},
	}

	for _, tt := range tbl {
		link, err := link(tt.inp)
		if err == nil && tt.err {
			t.Error("expected err =", tt.err)
		}
		if err != nil && !tt.err {
			t.Error("expected err =", tt.err)
		}
		if tt.link != link {
			t.Error("expected link", tt.link, "got", link)
		}
	}
}

func TestExcerpt(t *testing.T) {

	tbl := []struct {
		link    string
		excerpt string
		err     bool
	}{
		{"https://radio-t.com/p/2016/11/06/bot/", "В выпуске 520 была озвучена идея “сделай своего бота для любимого подкаста”. Я создал репо для этого дела где попытался описать как и что. Надеюсь, получилось понятно. В двух словах - каждый ваш бот это микро-рест запакованный в контейнер и получающий все сообщения из нашего чата. Если боту есть ...\\n\\n_Больше ботов, хороших и разных - Радио-Т Подкаст_", false},
		{"https://xxxx.radio-t.com blah2", "", true},
	}

	for _, tt := range tbl {
		ex, err := excerpt(tt.link)
		if err == nil && tt.err {
			t.Error("expected err =", tt.err)
		}
		if err != nil && !tt.err {
			t.Error("expected err =", tt.err)
		}
		if tt.excerpt != ex {
			t.Error("expected", tt.excerpt, "got", ex)
		}
	}

}
