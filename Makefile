.PHONY: up build down dependencies test logs static_analysis functional

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
	pip install -r requirements.txt
	pip install -r tests/requirements.txt

test: functional static_analysis

functional: dependencies up
	pytest --noconftest tests/functional

static_analysis: dependencies
	flake8
