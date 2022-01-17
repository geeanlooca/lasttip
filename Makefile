deploy:
	heroku container:push web --app=lasttip
	heroku container:release web --app=lasttip

dev:
	docker-compose up