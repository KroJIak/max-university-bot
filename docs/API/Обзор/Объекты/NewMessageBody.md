# NewMessageBody

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

## [](#Пример объекта)Пример объекта

JSON

Скопировать

`{ "text": "string", "attachments": [{ ... }], "link": { ... }, "notify": true, "format": "markdown" }`