# Back-end S Test Task

## Проєкт

Це система для імпорту товарів з XML-фідів (у форматі Rozetka), обробки їх через Celery, зберігання в PostgreSQL, кешування через Redis та доступу через API.

### Стек

- Python 3.13
- Django 5+
- Celery
- PostgreSQL
- Redis
- Docker + docker-compose
- modeltranslation
- ruff + black (linter & formatter)

---

## Швидкий старт

1. **Клонувати репозиторій:**

```bash
git clone <your-repo>
cd back-end-s-test-task
```

2. **Створити `.env` файл:**

```dotenv
DJANGO_SETTINGS_MODULE=config.settings
SECRET_KEY=some-django-secret
DEBUG=True
ALLOWED_HOSTS=*

POSTGRES_DB=roz_db
POSTGRES_USER=roz_user
POSTGRES_PASSWORD=password123
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/0
```

3. **Запуск через Docker:**

```bash
docker-compose up --build
```

4. **Запуск Celery воркера (в окремому терміналі):**

```bash
docker-compose exec web celery -A parser worker --loglevel=info
```

---

## ⚙️ Команди Makefile

| Команда                | Опис                                                                 |
|------------------------|----------------------------------------------------------------------|
| `make run`             | Запуск сервера розробки (на `127.0.0.1:8000`)                        |
| `make migrate`         | Застосування всіх міграцій                                           |
| `make makemigrations`  | Створення нових міграцій за змінами в моделях                        |
| `make createsuperuser` | Створення суперкористувача                                           |
| `make lint`            | Перевірка коду за допомогою `ruff`                                   |
| `make test`            | Запуск Django-тестів                                                 |
| `make parse-feeds`     | Запуск парсингу всіх активних фідів (асинхронно через Celery)        |
| `make shell`           | Запуск Django shell                                                  |
| `make format`          | Автоматичне форматування коду з `black` та `ruff`                    |
| `make collectstatic`   | Збір статичних файлів у `STATIC_ROOT`                                |
| `make worker`          | Запуск Celery worker                                                 |

---

## API

- `GET /api/v1/categories/` — список категорій верхнього рівня
- `GET /api/v1/categories/<id>/` — категорія + дочірні категорії + товари
- `GET /api/v1/products/` — фільтрація, пошук, сортування
- `GET /api/v1/products/<id>/` — деталі товару
- `GET /api/v1/stats/top-viewed-products/` — топ-10 найпопулярніших товарів за переглядами
- `GET /api/v1/stats/feeds/summary/` — загальний звіт по парсингу фідів (успішні, з помилками, активні)
- `GET /api/v1/stats/products/counts/` — кількість товарів у розрізі статусів: активні, чернетки, архів

---

## Тестування

```bash
make test
```

---

## Адмін-панель

- Доступна за `/admin/`
- Дозволяє керувати фідами, категоріями, товарами, атрибутами, зображеннями тощо.

---

## Примітки

- Підтримується мультимовність: українська, російська, англійська.
- Атрибути і категорії автоматично створюються під час парсингу.
- Парсинг підтримує звіти та статистику.

