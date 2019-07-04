dev:
	 docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

build:
	docker pull jonodrew/talent-tracker:latest

stop:
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml down

test:
	python3 -m flake8
	pytest
