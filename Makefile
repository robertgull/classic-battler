.PHONY: run get check format test setup-local-mongodb


run:
ifeq ($(OS),Windows_NT)
	cd src\my_app\ && set env=dev && uv run uvicorn main:app --reload
else
	cd src\my_app\ && env=dev uv run uvicorn main:app --reload
endif

get:
	powershell -Command "Invoke-RestMethod -Uri 'http://127.0.0.1:8000/todos/get' -Method GET"


check:
	uv run pyright src

format:
	uv run ruff check --fix src/
	uv run ruff format src/

test:
	uv run pytest -s .\tests\

setup-local-mongodb:
	podman machine stop
	podman machine start
	podman rm -i -f "petdb"
	podman run --detach --rm --name petdb -p 3000:27017 docker.io/mongodb/mongodb-community-server:latest