.PHONY: run get check format test setup-mongodb


run:
	uvicorn src.app.main:app --reload --log-level debug

get:
	powershell -Command "Invoke-RestMethod -Uri 'http://127.0.0.1:8000/todos/get' -Method GET"


check:
	uv run pyright src

format:
	uv run ruff check --fix src/ scripts/
	uv run ruff format src/

test:
	uv run pytest -s .\tests\

mongodb:
	podman machine stop
	podman machine start
	podman start petdb
