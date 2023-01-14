# demotivator-bot

### oops, some russian language :P

> Проект находится на стадии невероятно ранней разработки. \
> Воспользоваться ботом: [@yandex_demotivator_bot](https://t.me/yandex_demotivator_bot) \
> \
> По всем вопросам обращайтесь в Telegram: [@nesclass](https://t.me/nesclass)

## что это за хуета
demotivator-bot — это маленький локальный предновогодний челлендж,
цель которого являлось сделать минимальный жизнеспособный прототип (MVP)
знаменитого «Ржакабота» [@super_rjaka_demotivator_bot](https://t.me/super_rjaka_demotivator_bot).

## для суеверных и недоверчивых людей
1. Скачать исходный код проекта и установить зависимости (например, через [Poetry](https://python-poetry.org))
```bash
git clone https://github.com/nesclass/demotivator-bot
cd demotivator
poetry install
```
2. Добавить [токен Telegram-бота](https://t.me/BotFather) в переменные окружения: `BOT_TOKEN`
3. Разместить желаемый шрифт `./font.ttf` в корне проекта или прописать путь до шрифта в `FONT_PATH`

Готово! Теперь, по необходимости перейдя в виртуальную среду (например, с помощью команды `poetry shell`)
вы можете запустить бота командой `python -m bot` и наслаждаться собственным демотиватором без водяных знаков!

## как поддержать проект?
ручками.

- [x] переписать генерацию демотиваторов с ffmpeg на opencv
- [x] сделать уменьшение размера шрифта в зависимости от длины текста
- [ ] обработка пересланных сообщений с комментариями
- [ ] ttl, exception handling контекстного меню
- [ ] добавить выбор "оставить текущий текст"
- [ ] добавить вторую линию текста
- [ ] сделать генератор случайных текстов для демок
- [ ] переделать темп-файлы на буфферы (все файлы в озу)
- [ ] добавить возможность создавать демки с кумару через инлайн-меню
- [ ] оптимизация рантайма с помощью[`cv::parallel_for`](https://docs.opencv.org/4.x/dc/ddf/tutorial_how_to_use_OpenCV_parallel_for_new.html)

## а куда деньги на покушать

ltc: `LM6Ag8Z9MpfudRHh4jLBG7WRi9Vark4xJZ` \
tron: `TG7TAejtoPBFtiXcmwgt4w3u16Ruc61YDb`\
eth, bsc: `0xa0fEF871089d75D5E0821a17c955b83e038e06D1`

за остальными реквизитами в личку: [@nesclass](https://t.me/nesclass)