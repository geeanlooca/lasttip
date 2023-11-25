dev:
	docker-compose build flask-app
	docker-compose up -d

run:
	docker-compose build 
	docker-compose up -d


logs:
	docker-compose logs -f -t
