.PHONY: dev backend frontend test build clean install

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

dev:
	@echo "Start backend in one terminal: make backend"
	@echo "Start frontend in another: make frontend"
	@echo "Or docker-compose up"

test:
	cd backend && python -m pytest tests -v
	cd frontend && npm run build

build:
	cd frontend && npm run build

clean:
	rm -f backend/energy_brain.db
	rm -f backend/model_cache/*
	rm -rf frontend/dist frontend/node_modules/.vite

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
