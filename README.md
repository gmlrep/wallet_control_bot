# Wallet control bot

Бот дает возможность просматривать кошелек в сети TON прямо в телеграм боте. 
Так же в заданное время каждый день будут приходить сообщения с отчетом по каждому добавленному кошельку, при включении уведомлений в настройках бота.

![menu](img/menu.jpg)
![wallet_view](img/wallet_view.jpg)

## Используемые технологии
<div> 
<img src="https://img.shields.io/badge/Python-blue">
<img src="https://img.shields.io/badge/SQAlchemy-blue">
<img src="https://img.shields.io/badge/Pydentic-blue">
<img src="https://img.shields.io/badge/Alembic-blue">
<img src="https://img.shields.io/badge/Systemd-blue">
</div>

## Содержание

* [Особенности](#особенности)
* [Установка](#установка)

## Особенности
* Взаимодействие с  внешним TON API;
* Взаимодействие с базой данных при помощи SQLAlchemy ORM;
* Миграции базы данных с использованием Alembic.

## Установка

### Системные требования:
<div>
<img src="https://img.shields.io/badge/Python-3.10+-blue">
<img src="https://img.shields.io/badge/Linux/Windows-blue">
</div>

### Протестировать на своем локальном сервере (Linux):
1. Клонируйте репозиторий;
2. Перейдите (`cd`) в клонированный каталог и установите `uv`;
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
3. Создайте виртуальное окружение и установите зависимости:
```bash
uv sync
```
4. Совершите миграцию с помощью Alembic:
```bash
uv run alembic upgrade head
```
5. Скопируйте `.env-example` под именем `.env`, откройте его и заполните переменные;
6. Запустите бота:
```bash
uv run python -m bot
```

### Тесты
Запустить тесты локально:
```bash
uv run pytest
```

При необходимости можно экспортировать `requirements.txt` из `uv`-lock файла:
```bash
uv export --format requirements-txt --no-hashes --output-file requirements.txt
```

### Через Systemd
1. Выполните шаги 1-5 из раздела "Протестировать на своем локальном сервере" выше;
2. Скопируйте `wallet_control_bot.example.service` в `wallet_control_bot.service`, откройте и отредактируйте переменные `WorkingDirectory` 
и `ExecStart`;
3. Скопируйте (или создайте симлинк) файла службы в каталог `/etc/systemd/system/`;
4. Активируйте сервис и запустите его:
```bash
sudo systemctl enable wallet_control_bot
```
5. Проверьте, что сервис запустился:
```bash
sudo systemctcl status wallet_control_bot
```
