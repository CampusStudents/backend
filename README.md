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

2. Сгенерируйте jwt private и public ключи

```bash
mkdir src/certs
cd src/certs
openssl genrsa -out jwt-private.pem 2048
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```

3. Запустите сервисы:

```bash
docker compose up -d --build
```

## Переменные окружения (.env.example)

| Переменная                             | Описание                                                |
|----------------------------------------|---------------------------------------------------------|
| `PG_NAME`                              | Имя базы данных PostgreSQL контейнера                   |
| `PG_USER`                              | Пользователь PostgreSQL контейнера                      |
| `PG_PASSWORD`                          | Пароль пользователя PostgreSQL контейнера               |
| `APP__RUN__HOST`                       | Host для uvicorn/FastAPI                                |
| `APP__RUN__PORT`                       | Порт приложения                                         |
| `APP__DB__DRIVERNAME`                  | Драйвер БД                                              |
| `APP__DB__HOST`                        | Хост БД                                                 |
| `APP__DB__PORT`                        | Порт БД                                                 |
| `APP__DB__NAME`                        | Имя БД                                                  |
| `APP__DB__USER`                        | Пользователь БД                                         |
| `APP__DB__PASSWORD`                    | Пароль пользователя БД                                  |
| `APP__RBAC__INITIAL_SUBJECTS`          | Список ресурсов для генерации permissions (JSON-массив) |
| `APP__RBAC__INITIAL_ACTIONS`           | Список действий для генерации permissions (JSON-массив) |
| `APP__RBAC__INITIAL_PERMISSION_SCHEMA` | Схема ролей и scopes (JSON-словарь)                     |
| `APP__RBAC__ADMIN_EMAIL`               | Email администратора для bootstrap                      |
| `APP__RBAC__ADMIN_PASSWORD`            | Пароль администратора для bootstrap                     |
| `APP__RBAC__PUBLIC_ROLE_NAME`          | Название базовой роли (public)                          |
| `APP__RBAC__ADMIN_ROLE_NAME`           | Название роли администратора                            |
