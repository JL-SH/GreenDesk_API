.PHONY: help dev dev-down test logs migrate shell 

COMPOSE_DEV = docker compose -f docker-compose.yml
COMPOSE_TEST = docker compose -f docker-compose.test.yml --env-file .env.test

help: 
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Development ---
dev:  ## Start the development environment
	$(COMPOSE_DEV) up --build -d
	@echo "App at http://localhost:8000 | PgAdmin at http://localhost:5050"

dev-down:  ## Stop the development environment
	$(COMPOSE_DEV) down

logs:  ## Show app logs
	$(COMPOSE_DEV) logs -f app

migrate:  ## Run Alembic migrations in dev
	$(COMPOSE_DEV) exec app alembic upgrade head

shell:	## Open a terminal inside the app container
	$(COMPOSE_DEV) exec app bash

# --- Testing ---
test:  ## Run tests in isolated container
	$(COMPOSE_TEST) up --build --abort-on-container-exit --exit-code-from test
	$(COMPOSE_TEST) down -v

test-clean:  ## Clean test containers and images
	$(COMPOSE_TEST) down -v --rmi local
