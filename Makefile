.DEFAULT_GOAL := help

.PHONY: help
help:  ## Show this help message
	@echo ""
	@echo "PUCKHATE! Project Makefile"
	@echo "Usage: make [target]"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5); next } \
		/^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 }' \
		$(MAKEFILE_LIST)
	@echo ""

##@ Dev

MANAGEPY := docker compose run --rm backend uv run python manage.py
DOCKERRUNBE := docker compose run --rm --no-deps backend
DOCKERRUNFE := docker compose run --rm --no-deps frontend

.PHONY: dev
dev:  ## Bring up the local dev stack
	docker compose up --build

.PHONY: makemigrations
makemigrations:  ## Generate django migrations
	$(MANAGEPY) makemigrations

.PHONY: migrate
migrate:  ## Apply django migrations
	$(MANAGEPY) migrate

.PHONY: createsuperuser
createsuperuser:  ## Create a django superuser
	$(MANAGEPY) createsuperuser

.PHONY: manage
manage:  ## Run an arbitrary manage.py command, e.g. make manage ARGS="createsuperuser"
	$(MANAGEPY) $(ARGS)

.PHONY: clean
clean:  ## Remove build artifacts and local cache
	docker compose down --remove-orphans --rmi=local
	find . -type f -name "*.pyc" -delete
	find . -type d \( \
		-name "__pycache__" -o \
		-name ".ruff_cache" -o \
		-name ".ropeproject" -o \
		-name "private_media" \
	\) -exec rm -rf {} +

##@ Lint & Format

.PHONY: lint-be
lint-be:  ## Lint and type-check the backend (ruff + ty)
	$(DOCKERRUNBE) uv run ruff check .
	$(DOCKERRUNBE) uv run ruff format --check .
	$(DOCKERRUNBE) uv run ty check

.PHONY: format-be
format-be:  ## Format the backend (ruff)
	$(DOCKERRUNBE) uv run ruff format .

.PHONY: lint-fe
lint-fe:  ## Lint the frontend (eslint)
	$(DOCKERRUNFE) npm run lint

.PHONY: format-fe
format-fe:  ## Format the frontend (prettier)
	$(DOCKERRUNFE) npm run format

##@ Deployment

STAGING_HOST := ares
STAGING_DIR  := /opt/puckhate_staging
STAGING_COMPOSE := docker compose -f docker-compose.staging.yml --env-file .env.staging

.PHONY: secrets-hide
secrets-hide:  ## Encrypt secret files with git-secret
	git-secret hide -v -m

.PHONY: secrets-reveal
secrets-reveal:  ## Reveal secret files with git-secret
	git-secret reveal -f

.PHONY: deploy-staging
deploy-staging:  ## Rsync the repo to staging, then rebuild and restart the stack
	rsync -avz --delete \
		--exclude .venv \
		--exclude .ropeproject \
		--exclude .ruff_cache \
		--exclude .claude \
		--exclude docs \
		--exclude private_media \
		--exclude node_modules \
		--exclude __pycache__ \
		--exclude .git \
		--exclude .gitsecret \
		--exclude .env \
		. "$(STAGING_HOST):$(STAGING_DIR)/"
	ssh $(STAGING_HOST) "cd $(STAGING_DIR) && \
		$(STAGING_COMPOSE) build && \
		$(STAGING_COMPOSE) up -d && \
		$(STAGING_COMPOSE) restart scheduler"
