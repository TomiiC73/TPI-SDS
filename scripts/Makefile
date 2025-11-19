# Makefile para gestión de Docker - Banco Nacional
.PHONY: help build up down restart logs clean rebuild shell test

# Variables
DOCKER_COMPOSE = docker-compose
DOCKER = docker
APP_NAME = banco-nacional
ENUNCIADOS_NAME = banco-enunciados

# Colores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Mostrar esta ayuda
	@echo "$(GREEN)====================================="
	@echo "  Banco Nacional - Docker Commands"
	@echo "=====================================$(NC)"
	@echo ""
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

build: ## Construir las imágenes Docker
	@echo "$(GREEN)[INFO] Construyendo imágenes...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)[OK] Imágenes construidas$(NC)"

up: ## Iniciar los contenedores
	@echo "$(GREEN)[INFO] Iniciando contenedores...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)[OK] Contenedores iniciados$(NC)"
	@echo ""
	@echo "$(YELLOW)URLs de acceso:$(NC)"
	@echo "  - Banco:      http://localhost:5000"
	@echo "  - Enunciados: http://localhost:5001"
	@echo "  - DB Admin:   http://localhost:8080"

start: up ## Alias para 'up'

down: ## Detener y eliminar contenedores
	@echo "$(GREEN)[INFO] Deteniendo contenedores...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)[OK] Contenedores detenidos$(NC)"

stop: down ## Alias para 'down'

restart: ## Reiniciar los contenedores
	@echo "$(GREEN)[INFO] Reiniciando contenedores...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)[OK] Contenedores reiniciados$(NC)"

logs: ## Ver logs en tiempo real
	@echo "$(GREEN)[INFO] Mostrando logs (Ctrl+C para salir)$(NC)"
	$(DOCKER_COMPOSE) logs -f

logs-app: ## Ver logs solo de la app principal
	$(DOCKER_COMPOSE) logs -f banco-app

ps: ## Ver estado de los contenedores
	$(DOCKER_COMPOSE) ps

clean: ## Eliminar todo (contenedores, imágenes, volúmenes)
	@echo "$(RED)[WARNING] Esto eliminará TODOS los contenedores, imágenes y volúmenes$(NC)"
	@read -p "¿Estás seguro? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(GREEN)[INFO] Limpiando...$(NC)"; \
		$(DOCKER_COMPOSE) down -v --rmi all; \
		echo "$(GREEN)[OK] Limpieza completada$(NC)"; \
	else \
		echo "$(YELLOW)[INFO] Operación cancelada$(NC)"; \
	fi

rebuild: ## Reconstruir desde cero (sin cache)
	@echo "$(GREEN)[INFO] Reconstruyendo desde cero...$(NC)"
	$(DOCKER_COMPOSE) down
	$(DOCKER_COMPOSE) build --no-cache
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)[OK] Reconstrucción completada$(NC)"

shell: ## Acceder al shell del contenedor principal
	@echo "$(GREEN)[INFO] Accediendo al contenedor $(APP_NAME)$(NC)"
	$(DOCKER) exec -it $(APP_NAME) bash

shell-enunciados: ## Acceder al shell del contenedor de enunciados
	@echo "$(GREEN)[INFO] Accediendo al contenedor $(ENUNCIADOS_NAME)$(NC)"
	$(DOCKER) exec -it $(ENUNCIADOS_NAME) bash

db: ## Abrir SQLite en el contenedor
	@echo "$(GREEN)[INFO] Abriendo SQLite3$(NC)"
	$(DOCKER) exec -it $(APP_NAME) sqlite3 banco.db

backup-db: ## Hacer backup de la base de datos
	@echo "$(GREEN)[INFO] Creando backup...$(NC)"
	$(DOCKER) cp $(APP_NAME):/app/banco.db ./backup_banco_$(shell date +%Y%m%d_%H%M%S).db
	@echo "$(GREEN)[OK] Backup creado$(NC)"

restore-db: ## Restaurar base de datos desde backup
	@echo "$(YELLOW)[INFO] Ingresa el nombre del archivo de backup:$(NC)"
	@read -p "Archivo: " backup_file; \
	$(DOCKER) cp $$backup_file $(APP_NAME):/app/banco.db; \
	echo "$(GREEN)[OK] Base de datos restaurada$(NC)"

stats: ## Ver estadísticas de recursos
	$(DOCKER) stats --no-stream

inspect: ## Inspeccionar el contenedor principal
	$(DOCKER) inspect $(APP_NAME)

health: ## Verificar health status
	@echo "$(GREEN)[INFO] Estado de salud de los contenedores:$(NC)"
	@$(DOCKER) inspect --format='{{.Name}}: {{.State.Health.Status}}' $(APP_NAME) || echo "No health check"
	@$(DOCKER) inspect --format='{{.Name}}: {{.State.Health.Status}}' $(ENUNCIADOS_NAME) || echo "No health check"

network: ## Ver información de la red
	$(DOCKER) network inspect banco-network

all: build up ## Construir e iniciar todo

dev: ## Modo desarrollo (con logs)
	@echo "$(GREEN)[INFO] Iniciando en modo desarrollo...$(NC)"
	$(DOCKER_COMPOSE) up --build

prod: ## Preparar para producción
	@echo "$(YELLOW)[WARNING] Asegúrate de cambiar FLASK_ENV a 'production' en docker-compose.yml$(NC)"
	@echo "$(GREEN)[INFO] Construyendo para producción...$(NC)"
	$(DOCKER_COMPOSE) build --no-cache
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)[OK] Aplicación en producción$(NC)"

prune: ## Limpiar todo el sistema Docker
	@echo "$(RED)[WARNING] Esto limpiará TODO el sistema Docker$(NC)"
	@read -p "¿Estás seguro? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker system prune -a; \
	fi

# Default target
.DEFAULT_GOAL := help
