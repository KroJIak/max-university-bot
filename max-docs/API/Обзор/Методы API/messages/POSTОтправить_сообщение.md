# Отправить сообщение

POST`/messages`

Отправляет сообщение в чат

## [](#Прикрепление медиа)Прикрепление медиа

Медиафайлы прикрепляются к сообщениям поэтапно:

  1. Получите URL для загрузки медиафайлов
  2. Загрузите бинарные данные соответствующего формата по полученному URL
  3. После успешной загрузки получите JSON-объект в ответе. Используйте этот объект для создания вложения. Структура вложения:
     * `type`: тип медиа (например, `"video"`)
     * `payload`: JSON-объект, который вы получили

Пример для видео:

  1. Получите URL для загрузки

BASH

Скопировать

`curl -X POST 'https://botapi.max.ru/uploads?access_token=%access_token%&type=video' `

Ответ:

JSON

Скопировать

`{ "url": "https://vu.mycdn.me/upload.do…" } `

  2. Загрузите видео по URL

BASH

Скопировать

`curl -i -X POST -H "Content-Type: multipart/form-data" -F "data=@movie.mp4" "https://vu.mycdn.me/upload.do…" `

Ответ:

JSON

Скопировать

`{ "token": "_3Rarhcf1PtlMXy8jpgie8Ai_KARnVFYNQTtmIRWNh4" } `

  3. Отправьте сообщение с вложением

JSON

Скопировать

`{ "text": "Message with video", "attachments": [ { "type": "video", "payload": { "token": "_3Rarhcf1PtlMXy8jpgie8Ai_KARnVFYNQTtmIRWNh4" } } ] } `

## [](#Авторизация)Авторизация

`access_token`  
apiKey 

> Передача токена через query-параметры больше не поддерживается — используйте заголовок `Authorization: <token>`

Токен для вызова HTTP-запросов присваивается при создании бота — его можно найти в разделе платформы MAX для партнёров **Чат-бот и мини-приложение** → **Настроить**

Рекомендуем не разглашать токен посторонним, чтобы они не получили доступ к управлению ботом. Токен может быть отозван за нарушение Правил платформы

## [](#Параметры)Параметры

`user_id`  
integer  <int64> optional  

Если вы хотите отправить сообщение пользователю, укажите его ID

`chat_id`  
integer  <int64> optional  

Если сообщение отправляется в чат, укажите его ID

`disable_link_preview`  
boolean  optional  

Если `false`, сервер не будет генерировать превью для ссылок в тексте сообщения

## [](#Тело запроса)Тело запроса

`text`  
string  Nullable   

до `4000` символов

Новый текст сообщения

`attachments`  
AttachmentRequest[] Nullable   

Вложения сообщения. Если пусто, все вложения будут удалены

`link`  
object NewMessageLink Nullable

Ссылка на сообщение

`notify`  
boolean  optional  

По умолчанию: `true`

Если false, участники чата не будут уведомлены (по умолчанию `true`)

`format`  
enum TextFormat Nullable optional

Enum: `"markdown"` `"html"`

Если установлен, текст сообщения будет форматирован данным способом. Для подробной информации загляните в раздел [Форматирование](/docs-api#%D0%A4%D0%BE%D1%80%D0%BC%D0%B0%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5%20%D1%82%D0%B5%D0%BA%D1%81%D1%82%D0%B0)

## [](#Результат)Результат

`message`  
object Message

Сообщение в чате