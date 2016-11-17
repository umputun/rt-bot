package shows

import (
	"sync"
	"time"
)

func NewShows() *Shows {
	return &Shows{Items: []Show{}, ItemsByID: map[int]Show{}, mu: &sync.Mutex{}}
}

type Show struct {
	ID             int
	Date           time.Time
	URL            string
	TopicsMarkdown []string
	TopicsText     []string
	ImageURL       string
	ChatLogURL     string
	AudioURL       string
	TorrentURL     string
}

type ShowsByID map[int]Show

type Shows struct {
	Items     []Show
	ItemsByID map[int]Show
	mu        *sync.Mutex
}

func (s *Shows) Add(show Show) {
	s.mu.Lock()
	if _, exists := s.ItemsByID[show.ID]; !exists {
		s.Items = append(s.Items, show)
		s.ItemsByID[show.ID] = show
	}
	s.mu.Unlock()
}

func (s Shows) GetItems() []Show {
	return s.Items
}

func (s Shows) Last() Show {
	if len(s.Items) == 0 {
		return Show{}
	}
	return s.Items[len(s.Items)-1]
}

func (s Shows) Len() int {
	return len(s.Items)
}

func (s Shows) Swap(i, j int) {
	s.Items[i], s.Items[j] = s.Items[j], s.Items[i]
}

func (s Shows) Less(i, j int) bool {
	return s.Items[i].ID < s.Items[j].ID
}
