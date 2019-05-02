dev:
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

dev-build:
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml build

stop:
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml down