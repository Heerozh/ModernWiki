.PHONY: help build up down restart logs clean rebuild

# Default target
help:
	@echo "ModernWiki Management Commands:"
	@echo ""
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  restart   - Restart all services"
	@echo "  logs      - Show logs from all services"
	@echo "  clean     - Clean up containers and volumes"
	@echo "  rebuild   - Trigger site rebuild"
	@echo "  full      - Build images and start with site generation"
	@echo ""

# Build all Docker images
build:
	docker compose build

# Start all services (without initial build)
up:
	docker compose up -d

# Start all services including initial site build
full:
	docker compose --profile build up -d

# Stop all services
down:
	docker compose down

# Restart all services
restart:
	docker compose restart

# Show logs
logs:
	docker compose logs -f

# Clean up
clean:
	docker compose down -v --remove-orphans
	docker system prune -f

# Trigger manual site rebuild
rebuild:
	curl -X POST http://localhost/webhook || curl -X POST http://localhost:5000/rebuild

# Development mode (foreground with logs)
dev:
	docker compose --profile build up