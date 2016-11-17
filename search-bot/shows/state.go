package shows

import (
	"encoding/gob"
	"log"
	"os"

	"github.com/umputun/rt-bot/search-bot/config"
)

func Load() *Shows {
	if _, err := os.Stat(config.ShowsFilePath); os.IsNotExist(err) {
		return NewShows()
	}

	f, err := os.Open(config.ShowsFilePath)
	if err != nil {
		log.Println("Open gob file error: " + err.Error())
		return NewShows()
	}
	dec := gob.NewDecoder(f)
	var shows = NewShows()
	err = dec.Decode(shows)
	if err != nil {
		log.Println("Decode gob error: " + err.Error())
		return NewShows()
	}
	return shows
}

func Save(shows *Shows) error {
	f, err := os.Create(config.ShowsFilePath)
	if err != nil {
		return err
	}
	enc := gob.NewEncoder(f)
	err = enc.Encode(shows)
	if err != nil {
		return err
	}
	return nil
}
