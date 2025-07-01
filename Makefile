# Makefile для зручного керування Django-проєктом

PYTHON := python3.13
MANAGE := $(PYTHON) manage.py

run:
	$(MANAGE) runserver

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

createsuperuser:
	$(MANAGE) createsuperuser

lint:
	ruff check .

test:
	pytest

parse-feeds:
	$(MANAGE) shell -c "from tasks import process_all_feeds; process_all_feeds.delay()"

shell:
	$(MANAGE) shell

format:
	black .
	ruff check . --fix

collectstatic:
	$(MANAGE) collectstatic --noinput

worker:
	celery -A parser worker -l info