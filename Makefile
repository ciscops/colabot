# Makefile
PYTHON_EXE = python3
PROJECT_NAME="colabot"
LAMBDA_FUNCTION_NAME=""
TOPDIR = $(shell git rev-parse --show-toplevel)
PYDIRS_LAMBDA=awslambda
PYDIRS=$(PYDIRS_LAMBDA)
VENV = venv_$(PROJECT_NAME)
VENV_BIN=$(VENV)/bin
SRC_FILES := $(shell find $(PYDIRS) -name \*.py)

venv: ## Creates the needed virtual environment.
	test -d $(VENV) || virtualenv -p $(PYTHON_EXE) $(VENV) $(ARGS)

$(VENV): $(VENV_BIN)/activate ## Build virtual environment

$(VENV_BIN)/activate: requirements.txt test-requirements.txt
	test -d $(VENV) || virtualenv -p $(PYTHON_EXE) $(VENV)
	echo "export TOP_DIR=$(TOPDIR)" >> $(VENV_BIN)/activate
	. $(VENV_BIN)/activate; pip install -U pip; pip install -r requirements.txt -r test-requirements.txt

check-format: $(VENV)/bin/activate ## Check code format with black
	$(VENV_BIN)/black --diff --color .

format: $(VENV_BIN)/activate ## Format code using black
	$(VENV_BIN)/black $(PYDIRS)

pylint: $(VENV_BIN)/activate ## Run pylint
	$(VENV_BIN)/pylint --output-format=parseable --fail-under=9.98 --rcfile .pylintrc *.py $(PYDIRS)

clean: ## Clean venv
	$(RM) -rf $(VENV)
	$(RM) -rf docs/_build
	$(RM) -rf dist
	$(RM) -rf *.egg-info
	$(RM) -rf *.eggs
	$(RM) -rf docs/api/*
	find . -name "*.pyc" -exec $(RM) -rf {} \;
	$(RM) -f *.zip

clean-lambda: ## Clean lambda packages
	$(RM) -rf lambda-packages
	$(RM) lambda-packages.zip
	$(RM) lambda-function.zip

build: deps ## Builds EGG info and project documentation.
	$(VENV_BIN)/python setup.py egg_info

# create lambda-packages.zip using a docker image
lambda-packages-docker: clean-lambda
	docker run --rm --name lambda-docker-builder --user $$(id -u) -v $$(pwd):/build lambda-docker-builder:latest make lambda-packages.zip
	$(RM) -rf lambda-packages

lambda-packages: $(VENV) requirements.txt ## Install all libraries
	@[ -d $@ ] || mkdir -p $@/python # Create the libs dir if it doesn't exist
	. $(VENV_BIN)/activate ; SODIUM_INSTALL=system pip install -r requirements.txt -t $@/python

lambda-packages.zip: lambda-packages ## Output all code to zip file
	cd lambda-packages && zip -r ../$@ * # zip all python source code into output.zip

# Build lambda layer for colabot lambda function
lambda-layer-colabot: lambda-packages.zip
	aws lambda publish-layer-version \
	--layer-name $(LAMBDA_FUNCTION_NAME)-layer \
	--license-info "MIT" \
	--zip-file fileb://lambda-packages.zip \
	--compatible-runtimes python3.9
	$(RM) -rf lambda-packages

lambda-function-colabot.zip: lambda-handle.py ## Output all code to zip file
	zip -r $@ lambda-handle.py $(PYDIRS_LAMBDA) # zip all python source code into output.zip

# Upload layer for colabot lambda function
lambda-upload-colabot:lambda-function-colabot.zip ## Deploy all code to aws
	aws lambda update-function-code \
	--function-name $(LAMBDA_FUNCTION_NAME) \
	--zip-file fileb://lambda-function-colabot.zip

# Build image, needs to be done once, when initially making image
# make build-container
build-container:
	docker build -t lambda-docker-builder:latest . -f ./Dockerfile.builder

.PHONY: all clean $(VENV) test check format check-format pylint clean-docs-html clean-docs-markdown apidocs
