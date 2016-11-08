package search

import (
	"fmt"
	"strings"

	"strconv"

	"github.com/umputun/rt-bot/search-bot/config"
	"github.com/umputun/rt-bot/search-bot/shows"
	"github.com/blevesearch/bleve"
)

func NewIndex() (bleve.Index, error) {
	mapping := bleve.NewIndexMapping()
	return bleve.NewMemOnly(mapping)
}

func AddToIndex(index bleve.Index, show shows.Show) error {
	for i, topic := range show.TopicsText {
		err := index.Index(fmt.Sprintf("%d:%d", show.ID, i), topic)
		if err != nil {
			return err
		}
	}
	return nil
}

func ReindexAll(index bleve.Index, shows *shows.Shows) error {
	for _, show := range shows.GetItems() {
		err := AddToIndex(index, show)
		if err != nil {
			return err
		}
	}
	return nil
}

func Query(index bleve.Index, q string, allShows *shows.Shows) (string, error) {
	q = strings.Replace(q, "поиск", "", 1)
	q = strings.Replace(q, "!", "", -1)
	q = strings.TrimSpace(q)

	size := config.DefaultSearchResults

	// Check if results count set
	parts := strings.Split(q, ":")
	if len(parts) == 2 {
		if newSize, err := strconv.Atoi(parts[1]); err == nil {
			if newSize == 0 {
				newSize = config.DefaultSearchResults
			}
			if newSize > config.MaxSearchResults {
				newSize = config.MaxSearchResults
			}
			size = newSize
			q = parts[0]
		}
	}

	query := bleve.NewQueryStringQuery(q)
	searchRequest := bleve.NewSearchRequest(query)
	searchRequest.Size = size
	searchResult, err := index.Search(searchRequest)
	if err != nil {
		return "", err
	}

	out := ""
	if searchResult.Total == 0 {
		out = "Ничего не найдено"
	} else {
		for _, hit := range searchResult.Hits {
			if ok, showID, topicIdx := parseSearchId(hit.ID); ok {
				if len(allShows.ItemsByID[showID].TopicsMarkdown) > topicIdx {
					out = fmt.Sprintf("%s* [Выпуск %d](%s): %s\n",
						out,
						allShows.ItemsByID[showID].ID,
						allShows.ItemsByID[showID].URL,
						allShows.ItemsByID[showID].TopicsMarkdown[topicIdx])
				}
			}
		}
	}

	return out, nil
}

// Returns Show ID and Topic index
func parseSearchId(id string) (bool, int, int) {
	parts := strings.Split(id, ":")
	if len(parts) == 2 {
		if showID, err := strconv.Atoi(parts[0]); err == nil {
			if topicIdx, err := strconv.Atoi(parts[1]); err == nil {
				return true, showID, topicIdx
			}
		}
	}
	return false, 0, 0
}
