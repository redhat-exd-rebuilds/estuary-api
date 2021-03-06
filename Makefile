.PHONY: up build down test logs test infra static_analysis safety functional dependencies

down:
	docker-compose down -v

build:
	docker-compose build

up: build
	docker-compose up -d

logs: up
	docker-compose logs -f

infra: up
	tox -e infra

functional: up
	tox -e py36, py39

pin_dependencies:
	tox -e pin-dependencies

static_analysis:
	tox -e flake8, isort

safety:
	tox -e safety

test: up
	tox -r

dependencies:
	python -m pip install --upgrade pip
	pip install tox==3.23.0 docker-compose==1.28.5
