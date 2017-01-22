package shows

import (
	"strings"

	"strconv"

	"errors"

	"time"

	"fmt"

	"github.com/PuerkitoBio/goquery"
	"github.com/alehano/batch"
	"github.com/umputun/rt-bot/search-bot/config"
)

// GetShows gets shows data concurrently. Starts from "fromID" (excluded)
// Returns errors to "errHandler" function.
func Get(fromID int, errHandler func(error)) *Shows {
	shows := NewShows()
	showsLinks, err := fetchShowsLinks(fromID)
	if err != nil {
		errHandler(err)
		return shows
	}

	batch := batch.New(config.FetchWorkers, errHandler)
	batch.Start()

	for _, showURL := range showsLinks {
		fn := func(shows *Shows, url string) func() error {
			return func() error {
				show, err := fetchShow(url)
				if err != nil {
					return err
				} else {
					shows.Add(show)
				}
				return nil
			}
		}
		batch.Add(fn(shows, showURL))
	}

	batch.Close()
	return shows
}

func fetchShowsLinks(fromID int) ([]string, error) {
	links := []string{}

	doc, err := goquery.NewDocument(config.RadioTArchiveURL)
	if err != nil {
		return links, err
	}

	doc.Find("article h1 a").Each(func(i int, s *goquery.Selection) {
		if url, ok := s.Attr("href"); ok {
			if ok, id := parseTitle(s.Text()); ok {
				if fromID > 0 {
					if id > fromID {
						links = append(links, url)
					}
				} else {
					links = append(links, url)
				}
			}
		}
	})
	return links, nil
}

func fetchShow(url string) (Show, error) {
	show := Show{}

	doc, err := goquery.NewDocument(url)
	if err != nil {
		return show, err
	}

	if ok, id := parseTitle(doc.Find("h1.entry-title").Text()); ok {
		show.ID = id
	} else {
		return show, errors.New("Bad ID for: " + url)
	}

	show.URL = url

	allErr := []error{}
	doc.Find(".entry-content ul li").Each(func(i int, s *goquery.Selection) {

		topic := s.Text()
		show.TopicsText = append(show.TopicsText, topic)

		// Parse markdown
		s.Each(func(i int, s *goquery.Selection) {
			s.Find("a").Each(func(i int, s *goquery.Selection) {
				if link, ok := s.Attr("href"); ok {
					linkTxt := s.Text()
					mdLink := fmt.Sprintf("[%s](%s)", linkTxt, link)
					topic = strings.Replace(topic, linkTxt, mdLink, 1)
				}
			})
		})
		show.TopicsMarkdown = append(show.TopicsMarkdown, topic)
	})

	if dateS, ok := doc.Find(".meta time").Attr("datetime"); ok {
		if date, err := time.Parse(time.RFC3339, dateS); err == nil {
			show.Date = date
		}
	}

	if image, ok := doc.Find(".entry-content p img").Attr("href"); ok {
		show.ImageURL = image
	}

	doc.Find(".entry-content p a").Each(func(i int, s *goquery.Selection) {
		if link, ok := s.Attr("href"); ok {
			switch s.Text() {
			case "аудио":
				show.AudioURL = link
			case "radio-t.torrent":
				show.TorrentURL = link
			case "лог чата":
				show.ChatLogURL = link
			}
		}
	})

	if len(allErr) > 0 {
		return show, allErr[0]
	}
	return show, nil
}

func parseTitle(title string) (bool, int) {
	title = strings.TrimSpace(strings.ToLower(title))
	if strings.HasPrefix(title, "радио") {
		parts := strings.Fields(title)
		if len(parts) >= 2 {
			if num, err := strconv.Atoi(parts[1]); err == nil {
				return true, num
			}
		}
	}
	return false, 0
}
