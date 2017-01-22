tests:
	docker-compose run --rm app py.test
build:
	docker-compose build
