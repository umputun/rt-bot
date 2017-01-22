package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"regexp"
	"strconv"
	"strings"
	"time"
)

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
	Author   string   `json:"author"`
	Info     string   `json:"info"`
	Commands []string `json:"commands"`
}

var (
	commandReg = regexp.MustCompile(`^/random`)
	botName = "random-bot"
	botInfo    = info{
		"Ildar Gilfanov @rabinzon",
		"random-bot возвращает рандомное число или элемент списка. Вместе с ответом приходит рандомная строчка. " +
		"Пример ответа: `Я принял решение: 12`. Если не повезет, бот может не ответить, сославшись на занятость. ",
		[]string{
			"`/random` - рандомная строка: число от 0 до 100",
			"`/random min max` - рандомная строка: число от min до max",
			"`/random Umputun Ksenks Gray Bobuk` - рандомная строка: например Ksenks",
			"`/random да нет` - рандомная строка: да или нет"}}
)

func main() {
	http.HandleFunc("/", HandleInfo)
	http.HandleFunc("/info", HandleInfo)
	http.HandleFunc("/event", HandleEvent)

	log.Fatal(http.ListenAndServe(":8080", nil))
}

func random(min, max int) int {
	rand.Seed(time.Now().UTC().UnixNano())
	if max >= min {
		return rand.Intn(max-min) + min
	}

	return rand.Intn(min-max) + max
}

func GetRandom(s string) string {
	arr := strings.Fields(s)
	if len(arr) == 0 {
		return strconv.Itoa(random(0, 100))
	}
	index := random(0, len(arr))
	return arr[index]
}

func nothingToSay(w http.ResponseWriter) {
	w.WriteHeader(http.StatusExpectationFailed)
}

func HandleEvent(w http.ResponseWriter, r *http.Request) {
	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		nothingToSay(w)
		return
	}

	ev := event{}
	if err = json.Unmarshal(body, &ev); err != nil {
		nothingToSay(w)
		return
	}

	if commandReg.MatchString(ev.Text) {
		randomize(ev, w)
		return
	}
	nothingToSay(w)
}

func randomize(body event, w http.ResponseWriter) {
	digits, _ := regexp.Compile(`^\d+\s\d+$`)
	query := commandReg.ReplaceAllString(body.Text, "")
	queryRange := strings.Fields(digits.FindString(strings.TrimSpace(query)))

	if len(queryRange) > 0 {
		min, _ := strconv.Atoi(queryRange[0])
		max, _ := strconv.Atoi(queryRange[1])
		s := strconv.Itoa(random(min, max+1))
		sendResult(w, s)
		return
	}

	if len(query) > 0 {
		sendResult(w, GetRandom(query))
		return
	}

	s := strconv.Itoa(random(1, 100+1))

	sendResult(w, s)
}

func sendResult(w http.ResponseWriter, text string) {
	file, e := ioutil.ReadFile("./answers.json")
	if e != nil {
		fmt.Printf("File error: %v\n", e)
	}
	var st []string

	if er := json.Unmarshal(file, &st); er != nil {
		log.Fatal(er)
	}

	index := random(0, len(st))
	words := st[index]
	var answer string

	if words == "Чего надо? проваливай, я занят." {
		answer = words
	} else {
		answer = words + ": " + text
	}

	res, err := json.Marshal(response{Bot: botName, Text: answer})
	if err != nil {
		nothingToSay(w)
		return
	}

	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusCreated)
	fmt.Fprintf(w, "%s", string(res))
}

func HandleInfo(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusCreated)

	res, _ := json.Marshal(botInfo)

	fmt.Fprintf(w, "%s", string(res))
}
