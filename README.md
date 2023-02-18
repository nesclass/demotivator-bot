# demotivator-bot

> Project is currently in early developement stage. \
> Currently bot is deployed to [@yandex_demotivator_bot](https://t.me/yandex_demotivator_bot) \
> \
> Any questions: [@nesclass](https://t.me/nesclass)

## What is it?
demotivator-bot — is a small local challange,
which purpose was to create a minimal viable prototype (MVP)
of a well-known slavic-born «Ржакабот» [@super_rjaka_demotivator_bot](https://t.me/super_rjaka_demotivator_bot).

## How to?
1. Clone source code and install all the dependecies ([Poetry](https://python-poetry.org) used as an example)
```bash
git clone https://github.com/nesclass/demotivator-bot
cd demotivator
poetry install
```
2. Add [Telegram-bot API token](https://t.me/BotFather) to the env. config: `BOT_TOKEN`
3. Place your favorite font `./font.ttf` in the project's root folder, or enter an absolute font path using `FONT_PATH`

Done! Now, by your need you can move to a virtual environment (for example using `poetry shell`)
and run `python -m bot` to enjoy your demotivators without any watermarks.

## Contributions/TODO
- [x] Rewrite demotivators generation from ffmpeg to opencv
- [x] Decrease font size depending on text length
- [ ] Handle forwarded messages with comments 
- [ ] ttl, exception handling of context menu
- [ ] Add option "leave current text"
- [ ] Add second line of text
- [ ] Random text generation for demotivators
- [ ] move to BytesIO (buffer) from temporary files (all the data in memory)
- [ ] creating demotivators using inline menu 
- [ ] optimize runtime with [`cv::parallel_for`](https://docs.opencv.org/4.x/dc/ddf/tutorial_how_to_use_OpenCV_parallel_for_new.html)

## Donations

ltc: `LM6Ag8Z9MpfudRHh4jLBG7WRi9Vark4xJZ` \
tron: `TG7TAejtoPBFtiXcmwgt4w3u16Ruc61YDb`\
eth, bsc: `0xa0fEF871089d75D5E0821a17c955b83e038e06D1`

Other: [@nesclass](https://t.me/nesclass)
