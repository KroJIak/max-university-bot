# Update

Объект`Update` представляет различные типы событий, произошедших в чате. См. его наследников

`update_type`  
string    

message_created

`timestamp`  
integer  <int64>   

Unix-время, когда произошло событие

`message`  
object Message

Новое созданное сообщение

`user_locale`  
string  Nullable optional  

Текущий язык пользователя в формате IETF BCP 47. Доступно только в диалогах

## [](#Пример объекта)Пример объекта

JSON

Скопировать

`{ "update_type": "message_created", "timestamp": 0, "message": { ... }, "user_locale": "string" }`