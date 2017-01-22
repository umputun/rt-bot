package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"reflect"
	"regexp"
	"time"
)

const botID = "lucky"

type event struct {
	Text        string `json:"text"`
	Username    string `json:"username"`
	DisplayName string `json:"display_name"`
}

type response struct {
	Text string `json:"text"`
	Bot  string `json:"bot"`
}

func initPatterns() (*regexp.Regexp, *regexp.Regexp, *regexp.Regexp, *regexp.Regexp, *regexp.Regexp) {
	startPat, _ := regexp.Compile("(?i)lucky (start|go|begin)")
	stopPat, _ := regexp.Compile("(?i)lucky (stop|finish|results|done|over)")
	partPat, _ := regexp.Compile("(?i)(lucky?|want|gift|хочу|подарок)")
	adminPat, _ := regexp.Compile("(?i)^(umputun|bobuk|grayru|ksenks)$")
	statusPat, _ := regexp.Compile("(?i)^lucky (status|статус|\\?)$")
	return startPat, stopPat, partPat, adminPat, statusPat
}

func chooseWinner(participants map[string]bool) string {
	source := rand.NewSource(time.Now().UnixNano())
	random := rand.New(source)
	n := random.Intn(len(participants))
	return reflect.ValueOf(participants).MapKeys()[n].String()
}

func main() {
	log.Printf("Hello from lucky bot")
	participants := map[string]bool{}
	acceptVotes := false
	startPat, stopPat, partPat, adminPat, statusPat := initPatterns()

	process := func(text string, user string) (int, string) {
		isAdmin := adminPat.MatchString(user)

		if statusPat.MatchString(text) {
			message := "Розыгрыш завершен"
			if acceptVotes {
				message = fmt.Sprintf("Прием заявок в процессе, количество участников %d.",
					len(participants))
			}
			return http.StatusCreated, message
		} else if isAdmin && startPat.MatchString(text) && !acceptVotes {
			acceptVotes = true
			return http.StatusCreated, `Заявки на учатие в розыгрыше принимаются, пишем 'Хочу', голоса учитываются один раз`
		} else if isAdmin && stopPat.MatchString(text) && acceptVotes {
			acceptVotes = false
			message := "Никто не выявил желание получить подарок :("
			if len(participants) > 0 {
				winner := chooseWinner(participants)
				message = fmt.Sprintf("Розыгрыш завершен, учавствовали %d. Наш победитель %q, поздравляем!",
					len(participants), winner)
				participants = map[string]bool{}
			}
			return http.StatusCreated, message
		} else if !isAdmin && partPat.MatchString(text) && acceptVotes {
			participants[user] = true
			message := fmt.Sprintf("Заявка от участника %q принята!", user)
			return http.StatusCreated, message
		}
		return http.StatusExpectationFailed, ""
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

		status, text := process(ev.Text, ev.Username)
		resp := response{Bot: botID, Text: text}
		bresp, err := json.Marshal(resp)
		if err != nil {
			reportErr(err, w)
			return
		}

		log.Printf("%+v - %v - %s - %s", ev, time.Since(st), r.RemoteAddr, r.UserAgent())
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(status)
		fmt.Fprintf(w, "%s", string(bresp))
	})

	http.HandleFunc("/info", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(`{"author": "Zin4uk", "info": "
			Бот для розыгрыша призов в прямом эфире. Ведущий пишет
			'lucky start' и все желающие получить подарок пишут 'хочу',
			после ведущий пишет 'lucky stop' и случайным выбором из
			всех 'хотевших' определяется победитель. 'lucky status'
			- текущий статус розыгрыша"}`))
	})

	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatalf("failed to start server, %v", err)
	}
}
