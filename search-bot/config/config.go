package config

const (
	Port                 = ":8080"
	DefaultSearchResults = 5
	MaxSearchResults     = 30
	BotName              = "search-bot"
	RadioTURL            = "https://radio-t.com"
	RadioTArchiveURL     = RadioTURL + "/archives/"
	ShowsFilePath        = "./data/shows.gob"
	FetchWorkers         = 10
	Author               = "Alexey Khalyapin"
	Info                 = "Поиск по выпускам Радио-Т"
	Help                 = "В запросе поддерживаются `-` и `+` префиксы и маска `*`\\n" +
			"Примеры: `Выпуск 520`, `Поиск docker swarm`, `Поиск +яндекс* +google :10`"
)

var (
	Commans = []string{
		"Поиск - помощь",
		"Поиск [запрос[:число результатов]] - поиск по выпускам",
		"Выпуск [номер выпуска] - содержание выпуска",
	}
)
