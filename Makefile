.PHONY: run get check format test setup-mongodb



@if not exist .dummy ( podman ps --format "{{.Names}}" | findstr /C:"petdb" >nul ) else ( )


mongodb:
	podman machine stop || true
	podman machine start
	podman start petdb

run:
	@powershell -Command "if (-not (podman ps --format '{{.Names}}' | Select-String -Pattern '^petdb$$')) { Write-Host 'petdb not running, starting it...'; make mongodb } else { Write-Host 'petdb is already running.' }"
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
