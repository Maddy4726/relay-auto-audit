PYTHON := python3
PIP := $(PYTHON) -m pip

.PHONY: help install run clean refactor lint

help:
	@echo "Available targets:"
	@echo "  install    Install project dependencies"
	@echo "  run        Run the audit script over all PDFs in data/"
	@echo "  refactor   Format/cleanup Python source files"
	@echo "  lint       Run Python static analysis"
	@echo "  clean      Remove Python cache files"

install:
	$(PIP) install --upgrade pip
	$(PIP) install PyMuPDF black flake8

run:
	$(PYTHON) main.py

refactor:
	$(PYTHON) -m pip install --quiet black
	$(PYTHON) -m black .

lint:
	$(PYTHON) -m pip install --quiet flake8
	$(PYTHON) -m flake8 src main.py

clean:
	rm -rf __pycache__ src/__pycache__
	rm -f *.pyc src/*.pyc
