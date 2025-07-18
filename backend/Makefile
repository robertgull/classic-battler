.PHONY: run get check format test  mongodb cache cache



@if not exist .dummy ( podman ps --format "{{.Names}}" | findstr /C:"petdb" >nul ) else ( )


mongodb:
	podman machine stop || true
	podman machine start
	podman start petdb

cache:
	@powershell -Command \
		"if ((podman ps -a --format '{{.Names}}' | Select-String '^redis$$')) { \
			Write-Host 'Redis container already exists, starting it...'; \
			podman start redis; \
		} else { \
			Write-Host 'Creating and starting new Redis container...'; \
			podman run --name redis -p 6379:6379 -d redis; \
		}"

clear-cache:
	podman exec -it redis redis-cli FLUSHDB

run:
	$(MAKE) cache
	$(MAKE) clear-cache
	@powershell -Command "if (-not (podman ps --format '{{.Names}}' | Select-String -Pattern '^petdb$$')) { Write-Host 'petdb not running, starting it...'; make mongodb } else { Write-Host 'petdb is already running.' }"
	uvicorn src.app.main:app --reload --log-level debug

get:
	powershell -Command "Invoke-RestMethod -Uri 'http://127.0.0.1:8000/todos/get' -Method GET"


check:
	uv run pyright src

format:
	uv run ruff check --fix src/ scripts/ tests/
	uv run ruff format src/ scripts/ tests/

test:
	uv run pytest -s .\tests\
