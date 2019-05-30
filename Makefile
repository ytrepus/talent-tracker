dev:
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

dev-build:
	docker pull jonodrew/talent-tracker:latest

stop:
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml down
