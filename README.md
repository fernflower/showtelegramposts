# ShowTelegramPosts
A telegram bot/mongodb/static webpage generator app

## About
The project was an attempt to create a centralized registry of organized important information 
(both forwarded messages and unique content) that would be easily accessible without a telegram account.

## Getting started

1. Create and populate .env file with secrets

`cp .env.sample .env`

To create a telegram bot follow [official manual](https://core.telegram.org/bots).

2. Run docker-compose

`docker-compose up`


## To be done:
- [ ] Deploy at a subdomain at https://ciziproblem.cz
- [ ] Support image-only posts in telegram bot and web
- [ ] Support deleting posts by admins in webui
- [ ] Add ReplyKeyboardMarkup with available message types so the user can click one button only to categorize a post
