#!/bin/bash

dev:
	git stash
	git checkout master && git pull
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

build:
	docker pull jonodrew/talent-tracker:latest

stop:
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml down

test:
	python3 -m flake8
	pytest

ready:
	git stash
	black app/
	black migrations/
	black modules/
	black reporting/
	black scripts/
	black tests
	pip freeze > requirements.txt
	git add .
	git commit --allow-empty -m "Run black and generate requirements file"

