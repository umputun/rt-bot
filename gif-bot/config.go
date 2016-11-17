package main

const (
	BotId          = "gif-bot"
	Port           = "8080"
	MaxAttemps     = 10
	UrlRandomItem  = "http://developerslife.ru/random?json=true"
	BotAuthor      = "Igor Yatsenko"
	BotDescription = "Бот генерирует случайную gif картинку"
)

var BotCommands = []string{
	"показать гифку",
}
