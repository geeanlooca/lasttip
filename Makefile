test:
	docker compose up test

dev:
	docker-compose build flask-app
	docker-compose up -d

