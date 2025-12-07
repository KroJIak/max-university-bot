# Hello Bot

В этом разделе разберём пример реализации простого бота с использованием библиотеки MAX Bot API — напишем код для Hello Bot, чтобы научить его здороваться с пользователями

Больше примеров смотрите [в нашем репозитории на GitHub](https://github.com/max-messenger/max-bot-api-client-go)

1\. Создаём новый проект в терминале и устанавливаем библиотеку

BASH

Скопировать

`# Создаём новую папку для исходного кода вашего модуля Go и перейдите в неё mkdir my-first-bot cd my-first-bot # Запускаем свой модуль с помощью команды go mod init. go mod init first-max-bot # Устанавливаем библиотеку для работы с MAX API на golang go get github.com/max-messenger/max-bot-api-client-go `

Команда `go mod init` создает файл `go.mod` для отслеживания зависимостей вашего кода. Пока что файл включает только имя вашего модуля и версию Go, которую поддерживает ваш код.

2\. Создаём файл. Для GO — `bot.go`

3\. Создаём функцию main в пакете main — он обеспечит доступ к методам и утилитам

GO

Скопировать

`package main import ( "fmt" maxbot "github.com/max-messenger/max-bot-api-client-go" ) func main() { api := maxbot.New(os.Getenv("TOKEN")) // Some methods demo: info, err := api.Bots.GetBot() fmt.Printf("Get me: %#v %#v", info, err) } `

bot.go

4\. Закладываем функциональность приветствия — наш бот будет отвечать на команду `/hello`

GO

Скопировать

`package main import ( "fmt" maxbot "github.com/max-messenger/max-bot-api-client-go" ) func main() { api := maxbot.New(os.Getenv("TOKEN")) // Some methods demo: info, err := api.Bots.GetBot() fmt.Printf("Get me: %#v %#v", info, err) ctx, cancel := context.WithCancel(context.Background()) // создам  go func() { exit := make(chan os.Signal) signal.Notify(exit, os.Kill, os.Interrupt) <-exit cancel() }() for upd := range api.GetUpdates(ctx) { // Чтение из канала с обновлениями switch upd := upd.(type) { // Определение типа пришедшего обновления case *schemes.MessageCreatedUpdate: // Отправка сообщения  _, err := api.Messages.Send(maxbot.NewMessage().SetChat(upd.Message.Recipient.ChatId).SetText("Привет! ✨")) } } } `

bot.go

5\. Тестируем бота — отправляем команду `/hello`

![](/assets/hello_light.png) _Чат с Hello Bot_

Готово! Мы написали простого и дружелюбного Hello Bot. Воспользуйтесь возможностями и инструментами платформы MAX, чтобы запустить на платформе собственные проекты

  

![ℹ️](/assets/emoji/information_2139-fe0f.png) Если у вас возникли вопросы, [посмотрите раздел с ответами](/help)