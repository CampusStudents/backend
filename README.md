# Campus Backend
Платформа для поиска тиммейтов среди студентов под хакатоны, учебные проекты, стартапы и внутривузовские мероприятия.

## Команда

| ФИО                            | Роль     |
|--------------------------------|----------|
| Абдрафиков Амир Радикович      | Backend  |
| Габделганиев Расиль Фанисович  | Backend  |
| Лукманов Тимур Артурович       | Frontend |
| Кротова Анастасия Владимировна | Frontend |
| Тулыбаев Айгиз Айнурович       | Frontend |

## Быстрый старт

1. Создайте env-файл:
```bash
cp .env.example .env
```

2. Запустите сервисы:

```bash
docker compose up -d --build
```

## Переменные окружения (.env.example)

`PG_*` (для контейнера PostgreSQL):

- `PG_NAME`
- `PG_USER`
- `PG_PASSWORD`

`APP__RUN__*` (запуск приложения):

- `APP__RUN__HOST` - host для uvicorn/FastAPI
- `APP__RUN__PORT` - порт приложения

`APP__DB__*` (подключение SQLAlchemy):

- `APP__DB__DRIVERNAME` - драйвер БД
- `APP__DB__HOST` - хост
- `APP__DB__PORT` - порт
- `APP__DB__NAME` - имя
- `APP__DB__USER` - пользователь
- `APP__DB__PASSWORD` - пароль