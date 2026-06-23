### Hexlet tests and linter status:
[![Actions Status](https://github.com/NikitaSukharev/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/NikitaSukharev/python-project-83/actions)

## Page Analyzer

Веб-приложение для анализа страниц на SEO-пригодность. Позволяет добавлять сайты, проверять их доступность и извлекать SEO-данные (h1, title, meta description).

## Установка и запуск

```bash
# Установка зависимостей
make install

# Запуск в режиме разработки
make dev

# Запуск в продакшене
make start
```

## Переменные окружения

Скопируйте `.env.example` в `.env` и заполните значения:

```
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@localhost:5432/dbname
```

## База данных

```bash
psql -d $DATABASE_URL -f database.sql
```

## Деплой на Render

Команда сборки: `make build`  
Команда запуска: `make render-start`
