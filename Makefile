dev:
	docker pull jonodrew/talent-tracker:latest && docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

stop:
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml down

test:
	python3 -m flake8
	pytest
