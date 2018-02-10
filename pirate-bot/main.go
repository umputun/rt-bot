package main

import (
	"log"
	"net/http"
	"fmt"
	"time"
	"io/ioutil"
	"encoding/json"
	"errors"
	"regexp"
	"strings"
	"math/rand"
	"net/url"
)

const (
	botName = "pirate-bot"
	phraseCnt = 16
)
var phrases = [phraseCnt]string {
	"Arrrr!",
	"Yarrr!",
	"All hands on deck!",
	"Set full sail!",
	"Aye-Aye captain!",
	"Ahoy!",
	"Hoist the sails!",
	"Clap of thunder!",
	"Fire in the hole!",
	"Haul wind!",
	"Yo-ho-ho!",
	"Shiver me timbers!",
	"No prey, no pay!",
	"Weigh anchor!",
	"Dead men tell no tales.",
	"Yo-ho-ho, and a bottle of rum!"}

type event struct {
	Text        string `json:"text"`
	Username    string `json:"username"`
	DisplayName string `json:"display_name"`
}

type response struct {
	Text string `json:"text"`
	Bot  string `json:"bot"`
}

type info struct {
	Author string		`json:"author"`
	Info string			`json:"info"`
	Commands []string	`json:"commands"`
}

func main() {
	log.Printf("pirate-bot")

	reportErr := func(err error, w http.ResponseWriter) {
		w.WriteHeader(http.StatusExpectationFailed)
		fmt.Fprintf(w, "%v", err)
	}

	rand.Seed(time.Now().UnixNano())
	reAfter := regexp.MustCompile(`(пираты|послешоу|pirates|aftershow)\s*[#№]?(\d+)`)
	rePirate := regexp.MustCompile(`([^a-zA-Zа-яА-ЯёЁ]|^)(pirate(ss?|d)?|пират(ы|ов|а|у|е|ка)?|с?пирати(ть|л|ла|ли|ло)?|пиратск(ий|ая|ие|ую|ое|им|их|ого|ими))([^a-zA-Zа-яА-ЯёЁ]|$)`)
	reTorrent := regexp.MustCompile(`(torr?ent|торр?ент)\s*(.*)`)
	reCptnJack := regexp.MustCompile(`(капитан\s*джек\s*воробей|captain\s*jack\s*sparrow)`)
	reJack := regexp.MustCompile(`(джек\s*воробей|jack\s*sparrow)`)

	http.HandleFunc("/info", func(w http.ResponseWriter, r *http.Request) {
		resp := info {
			Author: "Mansiper",
			Info: "Самый пиратский бот! Arrrr!",
			Commands: []string{
				"пираты №X",
				"послешоу №X",
				"pirates #X",
				"aftershow #X",
				"Упомяни пирата",
			},
		}
		bresp, err := json.Marshal(resp)
		if err != nil {
			reportErr(err, w)
			return
		}

		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(bresp))
	})

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
		un := strings.ToLower(ev.Username)
		if un == botName || strings.Contains(un, "-bot") {
			reportErr(err, w)
			return
		}

		var answer, strTorrent, strAfter, strPirate string
		text := strings.ToLower(ev.Text)
		afterData := reAfter.FindStringSubmatch(text)
		if len(afterData) >= 3 {
			strAfter = afterData[2]
			log.Println("strAfter:", strAfter)
		} else {
			torrentData := reTorrent.FindStringSubmatch(text)
			if len(torrentData) >= 3 && torrentData[2] != "" {
				link, _ := url.Parse("https://rutracker.org/forum/tracker.php")
				params := url.Values{}
				params.Add("nm", torrentData[2])
				link.RawQuery = params.Encode()
				strTorrent = link.String()
				log.Println("strTorrent:", torrentData[2])
			} else {
				strPirate = rePirate.FindString(text)
				log.Println("strPirate:", strPirate)
			}
		}

		if strAfter != "" {
			answer = "[аудио](http://cdn.radio-t.com/rt" + strAfter + "post.mp3) ● [лог чата](http://chat.radio-t.com/logs/radio-t-" + strAfter + ".html) (но это не точно)"
		} else if strTorrent != "" {
			answer = "Yo-ho-ho and find me [torrent](" + strTorrent + ")!"
		} else if strPirate != "" {
			answer = phrases[rand.Intn(phraseCnt)]
		} else {
			strJack := reJack.FindString(text)
			log.Println("strJack:", strJack)
			if strJack != "" && reCptnJack.FindString(text) == "" {
				if strings.Contains(strJack, "jack") {
					answer = "Captain Jack Sparrow!"
				} else {
					answer = "Капитан Джек Воробей!"
				}
			}
		}

		if answer == "" {
			reportErr(errors.New("Empty result"), w)
			return
		}

		resp := response{
			Bot:  botName,
			Text: answer,
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