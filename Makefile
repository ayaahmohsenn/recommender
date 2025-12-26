up:
	docker compose up --build

down:
	docker compose down -v

test:
	cd services/django_app && pytest -q
	cd services/fastapi_app && pytest -q
