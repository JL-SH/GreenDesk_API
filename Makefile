.PHONY: help dev dev-down test logs migrate

COMPOSE_DEV = docker compose -f docker-compose.yml
COMPOSE_TEST = docker compose -f docker-compose.test.yml --env-file .env.test

help: 
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Desarrollo ---
dev:  ## Levanta el entorno de desarrollo
	$(COMPOSE_DEV) up --build -d
	@echo "App en http://localhost:8000 | PgAdmin en http://localhost:5050"

dev-down:  ## Para el entorno de desarrollo
	$(COMPOSE_DEV) down

logs:  ## Muestra logs de la app
	$(COMPOSE_DEV) logs -f app


migrate:  ## Ejecuta migraciones de Alembic en dev
	$(COMPOSE_DEV) exec app alembic upgrade head

# --- Testing ---
test:  ## Ejecuta los tests en contenedor aislado
	$(COMPOSE_TEST) up --build --abort-on-container-exit --exit-code-from test
	$(COMPOSE_TEST) down -v

test-clean:  ## Limpia contenedores e imágenes de test
	$(COMPOSE_TEST) down -v --rmi local
