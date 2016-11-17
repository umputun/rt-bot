package main

import (
	"strconv"
	"strings"
	"time"

	"github.com/umputun/rt-bot/search-bot/search"
	"github.com/umputun/rt-bot/search-bot/shows"
	"github.com/blevesearch/bleve"

	"log"

	"net/http"

	"sort"

	"encoding/json"

	"fmt"

	"github.com/umputun/rt-bot/search-bot/config"
	"gopkg.in/robfig/cron.v2"
)

var (
	searchIndex bleve.Index
	allShows    *shows.Shows
)

type reqData struct {
	Text        string `json:"text"`
	Username    string `json:"username"`
	DisplayName string `json:"display_name"`
}

type respData struct {
	Text string `json:"text"`
	Bot  string `json:"bot"`
}

type infoData struct {
	Author   string   `json:"author"`
	Info     string   `json:"info"`
	Commands []string `json:"commands"`
}

func main() {
	allShows = shows.Load()

	newSearchIndex, err := search.NewIndex()
	if err != nil {
		log.Fatal("Search index create error:", err)
	}
	searchIndex = newSearchIndex
	err = search.ReindexAll(searchIndex, allShows)
	if err != nil {
		log.Fatal("Search reindex error:", err)
	}

	// Update if last show was more than 7 days ago
	if allShows.Last().Date.Add(7 * 24 * time.Hour).Before(time.Now()) {
		update(allShows, searchIndex)
	}

	// Update every Monday at 6:00
	c := cron.New()
	_, err = c.AddFunc("0 6 * * * 1", func() {
		update(allShows, searchIndex)
	})
	if err != nil {
		log.Fatal("Add to cron error:", err)
	}

	// Run server
	log.Printf("%s\n", config.BotName)
	log.Printf("Total shows: %d, last show #%d\n", allShows.Len(), allShows.Last().ID)
	log.Printf("Bot running at %s\n", config.Port)

	http.HandleFunc("/event", panicRecover(eventHandler))
	http.HandleFunc("/info", panicRecover(infoHandler))
	if err := http.ListenAndServe(config.Port, nil); err != nil {
		log.Fatalf("failed to start server, %v", err)
	}
}

func panicRecover(f func(w http.ResponseWriter, r *http.Request)) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if r := recover(); r != nil {
				log.Printf("PANIC:%s\\n", r)
			}
		}()
		f(w, r)
	}
}

func update(allShows *shows.Shows, index bleve.Index) {
	log.Println("Updating...")

	newShows := shows.Get(allShows.Last().ID, func(err error) {
		log.Println(err)
	})

	count := 0
	for _, show := range newShows.GetItems() {
		allShows.Add(show)
		err := search.AddToIndex(index, show)
		if err != nil {
			log.Println(err)
		}
		count++
	}

	sort.Sort(allShows)

	err := shows.Save(allShows)
	if err != nil {
		log.Println(err)
	}
	log.Printf("%d show(s) updated\\n", count)
}

func reportErr(err error, w http.ResponseWriter) {
	w.WriteHeader(http.StatusExpectationFailed)
	if err != nil {
		fmt.Fprintf(w, "%v", err)
	}
}

func jsonResponse(w http.ResponseWriter, code int, data interface{}) {
	out, err := json.Marshal(data)
	if err != nil {
		reportErr(err, w)
		return
	}
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(code)
	fmt.Fprintf(w, "%s", out)
}

func eventHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		return
	}

	decoder := json.NewDecoder(r.Body)
	var rd reqData
	err := decoder.Decode(&rd)
	if err != nil {
		reportErr(err, w)
		return
	}
	defer r.Body.Close()

	answer, err := query(strings.ToLower(rd.Text))
	if err != nil || answer == "" {
		reportErr(err, w)
		return
	}

	// Add extra new line first
	answer = "\\n" + answer

	jsonResponse(w, http.StatusCreated, respData{Text: answer, Bot: config.BotName})
}

func infoHandler(w http.ResponseWriter, r *http.Request) {
	jsonResponse(w, http.StatusOK, infoData{
		Author:   config.Author,
		Info:     config.Info,
		Commands: config.Commans,
	})
}

func query(q string) (string, error) {
	if strings.HasPrefix(q, "поиск") && strings.HasSuffix(q, "!") {
		q = strings.Replace(q, "поиск", "", 1)
		q = strings.Replace(q, "!", "", -1)
		q = strings.TrimSpace(q)

		if q == "" {
			return getHelp()
		}

		return search.Query(searchIndex, q, allShows)
	}

	if strings.HasPrefix(q, "выпуск") && strings.HasSuffix(q, "!") {
		return getShowDetail(q)
	}

	return "", nil
}

func getHelp() (string, error) {
	help := config.Help
	help += "\\n\\n**Команды:**\\n"
	for _, cmd := range config.Commans {
		help += cmd + "\\n"
	}
	return help, nil
}

func getShowDetail(q string) (string, error) {
	q = strings.Replace(q, "выпуск", "", 1)
	q = strings.Replace(q, "!", "", -1)
	q = strings.TrimSpace(q)
	num, err := strconv.Atoi(q)
	if err != nil {
		return "", nil
	}
	if show, ok := allShows.ItemsByID[num]; ok {
		out := fmt.Sprintf("**[Выпуск %d](%s)**\\n", show.ID, show.URL)
		for _, topic := range show.TopicsMarkdown {
			out = fmt.Sprintf("%s* %s\\n", out, topic)
		}
		if show.AudioURL != "" {
			out = fmt.Sprintf("%s[аудио](%s)", out, show.AudioURL)
		}
		if show.TorrentURL != "" {
			out = fmt.Sprintf("%s | [torrent](%s)", out, show.TorrentURL)
		}
		if show.ChatLogURL != "" {
			out = fmt.Sprintf("%s | [лог чата](%s)", out, show.ChatLogURL)
		}
		return out, nil
	}
	return "", nil
}
