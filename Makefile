.PHONY: up build down dependencies test logs

down:
	docker-compose down -v

build:
	docker-compose build

up: build
	docker-compose up -d

logs: up
	docker-compose logs -f

dependencies:
	pip install --upgrade pip
	pip install -r tests/requirements.txt

test: dependencies up
	pytest --noconftest tests/functional
