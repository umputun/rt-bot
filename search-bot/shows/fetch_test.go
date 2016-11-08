package shows

import (
	"fmt"
	"testing"
)

//func TestGetShows(t *testing.T) {
//	shows := GetShows(0, func(err error) {
//		fmt.Println(err)
//	})
//	fmt.Println(shows)
//}

func TestFetchShowsLinks(t *testing.T) {
	links, err := fetchShowsLinks(0)
	if err != nil {
		t.Error(err)
	}
	for _, link := range links {
		fmt.Println(link)
	}

}

//func TestFetchShow(t *testing.T) {
//	show, err := fetchShow(radioTURL + "/p/2013/04/27/podcast-338/")
//	if err != nil {
//		t.Error(err)
//	}
//	fmt.Println(show)
//}
