deploy:
	heroku container:push web --app=lasttip
	heroku container:release web --app=lasttip

test:
	docker compose up test

dev:
	docker-compose up