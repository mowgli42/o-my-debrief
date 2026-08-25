.PHONY: install fixtures test backend frontend recorder demo capture

DEBRIEF_API_PORT ?= 8020
DEBRIEF_UI_PORT ?= 5173

install:
	python3 -m venv .venv
	.venv/bin/pip install -e ".[test]"
	cd frontend && npm install

fixtures:
	.venv/bin/python -m omy_debrief.demo.generate --out data/debrief

test: fixtures
	PYTHONPATH=src .venv/bin/pytest -q

backend: fixtures
	DEBRIEF_DATA_DIR=data/debrief PYTHONPATH=src .venv/bin/uvicorn omy_debrief.api.app:app --host 0.0.0.0 --port $(DEBRIEF_API_PORT) --reload

frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port $(DEBRIEF_UI_PORT)

recorder:
	.venv/bin/python -m omy_debrief.recorder.cli --mode demo --out data/debrief

demo: fixtures
	@echo "API :$(DEBRIEF_API_PORT)  UI :$(DEBRIEF_UI_PORT)  — run make backend and make frontend in separate terminals"
	@echo "Swagger: http://127.0.0.1:$(DEBRIEF_API_PORT)/docs"
	@echo "On a full o-my suite host, keep 8020 for debrief; o-my remaps classification-guard to :8041."

capture:
	cd frontend && node ../scripts/capture-screenshots.mjs
