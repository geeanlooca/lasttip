dev:
	docker-compose build flask-app
	docker-compose up -d

run:
	docker-compose up --build -d


logs:
	docker-compose logs -f -t
