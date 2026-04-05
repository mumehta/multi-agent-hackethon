.PHONY: help sync sync-dev backend frontend starter test lint lint-fix check lock

PYTHON ?= python
UV ?= uv
BACKEND_APP ?= src.multi_agent.api.main:app
FRONTEND_APP ?= frontend/app.py

help: ## Show available targets and what they do
	@echo Available targets:
	@$(PYTHON) -c "import pathlib,re,sys; pattern=re.compile(r'^([a-zA-Z0-9_-]+):.*## (.+)$$'); entries=[f'  {m.group(1):<10} - {m.group(2)}' for file_name in sys.argv[1:] for line in pathlib.Path(file_name).read_text().splitlines() for m in [pattern.match(line)] if m]; print('\n'.join(entries))" $(MAKEFILE_LIST)

sync: ## Install runtime dependencies from the root uv project
	$(UV) sync

sync-dev: ## Install runtime and dev dependencies from the root uv project
	$(UV) sync --dev

backend: ## Run the backend API with live reload
	$(UV) run uvicorn $(BACKEND_APP) --reload

frontend: ## Run the Streamlit frontend from the project root
	$(UV) run streamlit run $(FRONTEND_APP)

starter: ## Run the package entrypoint script
	$(UV) run multi-agent-suite

test: ## Run the test suite with pytest
	$(UV) run pytest

lint: ## Run Ruff checks across the repository
	$(UV) run ruff check .

lint-fix: ## Run Ruff and auto-fix issues where possible
	$(UV) run ruff check . --fix

check: ## Parse-check frontend Python files with py_compile
	$(UV) run $(PYTHON) -m py_compile frontend/app.py frontend/utils/api_client.py frontend/utils/constants.py frontend/utils/data_access.py frontend/utils/formatters.py frontend/utils/mock_data.py frontend/utils/state.py frontend/utils/view_helpers.py frontend/pages/1_Home.py frontend/pages/2_Upload_Analyze.py frontend/pages/3_Incident_Explorer.py frontend/pages/4_Cookbook.py frontend/pages/5_Timeline_Root_Cause.py frontend/pages/6_Workflow_Graph.py frontend/pages/7_Artifacts_Exports.py frontend/pages/8_Integrations.py frontend/pages/9_Runs_History.py

lock: ## Refresh the root uv.lock file
	$(UV) lock
