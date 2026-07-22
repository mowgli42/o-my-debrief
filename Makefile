.PHONY: install fixtures test backend frontend recorder demo capture

install:
	python3 -m venv .venv
	.venv/bin/pip install -e ".[test]"
	cd frontend && npm install

fixtures:
	.venv/bin/python -m omy_debrief.demo.generate --out data/debrief

test: fixtures
	PYTHONPATH=src .venv/bin/pytest -q

backend: fixtures
	DEBRIEF_DATA_DIR=data/debrief PYTHONPATH=src .venv/bin/uvicorn omy_debrief.api.app:app --host 0.0.0.0 --port 8020 --reload

frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

recorder:
	.venv/bin/python -m omy_debrief.recorder.cli --mode demo --out data/debrief

demo: fixtures
	@echo "API :8020  UI :5173  — run make backend and make frontend in separate terminals"
	@echo "Swagger: http://127.0.0.1:8020/docs"

capture:
	cd frontend && node ../scripts/capture-screenshots.mjs
