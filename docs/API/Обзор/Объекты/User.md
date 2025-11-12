# User

Объект, описывающий пользователя. Имеет несколько вариаций (наследований):

  * [`User`](/docs-api/objects/User)
  * [`UserWithPhoto`](/docs-api/objects/UserWithPhoto)
  * [`BotInfo`](/docs-api/objects/BotInfo)
  * [`ChatMember`](/docs-api/objects/ChatMember)

`user_id`  
integer  <int64>   

ID пользователя

`first_name`  
string    

Отображаемое имя пользователя

`last_name`  
string  Nullable   

Отображаемая фамилия пользователя

`name`  
string  Nullable optional  

 _Устаревшее поле, скоро будет удалено_

`username`  
string  Nullable   

Уникальное публичное имя пользователя. Может быть `null`, если пользователь недоступен или имя не задано

`is_bot`  
boolean    

`true`, если пользователь является ботом

`last_activity_time`  
integer  <int64>   

Время последней активности пользователя в MAX (Unix-время в миллисекундах). Может быть неактуальным, если пользователь отключил статус "онлайн" в настройках.

## [](#Пример объекта)Пример объекта

JSON

Скопировать

`{ "user_id": 0, "first_name": "string", "last_name": "string", "name": "string", "username": "string", "is_bot": true, "last_activity_time": 0 }`