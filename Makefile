.PHONY help up down logs test

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  up         Build and start container in the background"
	@echo "  down       Stop and remove container"
	@echo "  logs       Logs for the web service"
	@echo "  test       Run pytest suite inside the fraud_service container"

up:
    docker-compose up --build -d

down:
    docker-compose down

logs:
    docker-compose logs -f fraud_service

test:
    docker-compose exec fraud_service pytest

