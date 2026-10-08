.PHONY: help install test lint check-tools regression demo clean docker-build docker-run

PYTHON ?= python
PYTEST ?= pytest

help:
	@echo "PHYFlow — EDA Automation & Custom-Cell Validation Framework"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       Install PHYFlow in editable mode"
	@echo "  make check-tools   Verify availability of EDA and system tools"
	@echo "  make test          Run pytest unit, integration, and regression tests"
	@echo "  make lint          Run syntax and style checks"
	@echo "  make regression    Execute full regression suite using PHYFlow CLI"
	@echo "  make demo          Launch Streamlit engineering dashboard"
	@echo "  make docker-build  Build Docker image for EDA environment"
	@echo "  make docker-run    Run PHYFlow inside Docker container"
	@echo "  make clean         Remove temporary build files and run logs"

install:
	$(PYTHON) -m pip install -e .

check-tools:
	$(PYTHON) -m phyflow cli check-tools

test:
	$(PYTEST) -v tests/

lint:
	$(PYTHON) -m ruff check phyflow/ tests/ || true

regression:
	$(PYTHON) -m phyflow cli regression --config configs/regression.yaml --workers 4

demo:
	streamlit run dashboard/app.py

docker-build:
	docker build -t phyflow:latest .

docker-run:
	docker run --rm -it -v $(shell pwd):/workspace phyflow:latest phyflow check-tools

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache runs/ *.db
	find . -type d -name "__pycache__" -exec rm -rf {} +
