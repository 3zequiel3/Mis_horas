.PHONY: build up down restart logs shell-backend shell-frontend db-backup db-restore clean
start:
	@echo "Iniciando Mis Horas..."
	docker compose build --no-cache
	docker compose up -d
	@echo "✅ Servicios levantados"
	@echo "Frontend:  http://localhost:21000"
	@echo "Backend:   http://localhost:21050"

restart:
	docker compose restart
	@echo "🔄 Servicios reiniciados"

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

logs-db:
	docker compose logs -f db

bash-backend:
	docker compose exec backend bash

bash-frontend:
	docker compose exec frontend sh

bash-db:
	docker compose exec db mysql -u mis_horas -p

clean:
	docker compose down -v
	@echo "✅ Contenedores y volúmenes eliminados"

rebuild: clean start
	@echo "✅ Limpieza completa y reconstrucción"

ps:
	docker compose ps
