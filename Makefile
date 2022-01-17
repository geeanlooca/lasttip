deploy:
	docker-compose -f production.yml build
	heroku container:push web --app=lasttip
	heroku container:release web --app=lasttip

dev:
	docker-compose up