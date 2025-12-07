# Hello Bot

В этом разделе разберём пример реализации простого бота с использованием библиотеки MAX Bot API — напишем код для Hello Bot, чтобы научить его здороваться с пользователями

Больше примеров смотрите [в нашем репозитории на GitHub](https://github.com/max-messenger/max-bot-api-client-ts)

1\. Создаём новый проект в терминале и устанавливаем библиотеку для своего менеджера пакетов. Используем скрипт `curl` или `wget`

BASH

Скопировать

`# Создайте папку и перейдите в неё mkdir my-first-bot cd my-first-bot # Установите MAX Bot API # Для npm npm install --save @maxhub/max-bot-api # Для yarn yarn add @maxhub/max-bot-api # Для pnpm pnpm add @maxhub/max-bot-api # Для deno deno add npm:@maxhub/max-bot-api # Установите и настройте TypeScript (опционально) yarn add -D typescript npx tsc --init `

2\. Создаём файл. Для JavaScript — `bot.js`, для TypeScript — `bot.ts`

3\. Создаём объект класса Bot — он обеспечит доступ к методам и утилитам

JS

Скопировать

`import { Bot } from '@maxhub/max-bot-api'; const bot = new Bot(process.env.BOT_TOKEN); // Токен, полученный при регистрации бота в MAX bot.start(); // Запускает получение обновлений `

bot.js

4\. Закладываем функциональность приветствия — наш бот будет отвечать на команду `/hello`

JS

Скопировать

`import { Bot } from '@maxhub/max-bot-api'; const bot = new Bot(process.env.BOT_TOKEN); // Устанавливает список команд, который пользователь будет видеть в чате с ботом bot.api.setMyCommands([ { name: 'hello', description: 'Поприветствовать бота', }, ]); // Обработчик команды '/hello' bot.command('hello', (ctx) => { return ctx.reply('Привет! ✨'); }); bot.start(); `

bot.js

5\. Тестируем бота — отправляем команду `/hello`

![](/assets/hello_light.png) _Чат с Hello Bot_

6\. Сделаем приветствие адресным — укажем имя пользователя, который отправил сообщение, и проверим результат командой `/hello`

JS

Скопировать

`import { Bot } from '@maxhub/max-bot-api'; const bot = new Bot(process.env.BOT_TOKEN); bot.api.setMyCommands([ { name: 'hello', description: 'Поприветствовать бота', }, ]); bot.command('hello', (ctx) => { const user = ctx.user(); // Получаем данные пользователя из нового события if (!user) { // Если пользователя не получилось определить, просто поздороваемся  return ctx.reply('Привет! ✨'); } // Если пользователя определён, поздороваемся адресно return ctx.reply(`Привет, ${ctx.user()}! ✨`); }); bot.start(); `

bot.js

Готово! Мы написали простого и дружелюбного Hello Bot. Воспользуйтесь возможностями и инструментами платформы MAX, чтобы запустить на платформе собственные проекты

![](/assets/hello_name_light.png) _Чат с Hello Bot_

  

![ℹ️](/assets/emoji/information_2139-fe0f.png) Если у вас возникли вопросы, [посмотрите раздел с ответами](/help)