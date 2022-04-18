# Makefile
PYTHON_EXE = python3
PROJECT_NAME="colabot"
TOPDIR = $(shell git rev-parse --show-toplevel)
PYDIRS_CARDS=cards
PYDIRS_FEATURES=features
PYDIRS_WEBEX=webex
PYDIRS=$(PYDIRS_CARDS) $(PYDIRS_FEATURES) $(webex)
VENV = venv_$(PROJECT_NAME)
VENV_BIN=$(VENV)/bin

venv: ## Creates the needed virtual environment.
	test -d $(VENV) || virtualenv -p $(PYTHON_EXE) $(VENV) $(ARGS)

$(VENV): $(VENV_BIN)/activate ## Build virtual environment

$(VENV_BIN)/activate: requirements.txt test-requirements.txt
	test -d $(VENV) || virtualenv -p $(PYTHON_EXE) $(VENV)
	echo "export TOP_DIR=$(TOPDIR)" >> $(VENV_BIN)/activate
	. $(VENV_BIN)/activate; pip install -U pip; pip install -r requirements.txt -r test-requirements.txt

check-format: $(VENV)/bin/activate ## Check code format with black
	@( \
	set -eu pipefail ; set -x ;\
	DIFF=`$(VENV)/bin/black --diff --color $(PYDIRS)` ;\
	if [ -n "$$DIFF" ] ;\
	then \
	echo -e "\nFormatting changes requested:\n" ;\
	echo "$$DIFF" ;\
	echo -e "\nRun 'make format' to automatically make changes.\n" ;\
	exit 1 ;\
	fi ;\
	)

format: $(VENV_BIN)/activate ## Format code using black
	$(VENV_BIN)/black $(PYDIRS)


pylint: $(VENV_BIN)/activate ## Run pylint
	$(VENV_BIN)/pylint --output-format=parseable --rcfile .pylintrc *.py $(PYDIRS)
