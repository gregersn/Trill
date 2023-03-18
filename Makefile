BUILD_DIR := ./dist
VERSION := 0.0.6
PACKAGE_NAME := trill
SOURCE_PACKAGE_NAME := $(PACKAGE_NAME)-$(VERSION).tar.gz
WHEEL_PACKAGE_NAME := $(PACKAGE_NAME)-$(VERSION)-py3-none-any.whl

SOURCE_PACKAGE := $(BUILD_DIR)/$(SOURCE_PACKAGE_NAME)
WHEEL_PACKAGE := $(BUILD_DIR)/$(WHEEL_PACKAGE_NAME)

.PHONY: init
init: .venv/pyvenv.cfg .requirements

# More or less random choice of dependency to be depending on something.
.venv/pyvenv.cfg: pyproject.toml
	python3 -m venv .venv

.requirements: .venv/pyvenv.cfg requirements-dev.txt
	.venv/bin/python3 -m pip install -r requirements-dev.txt
	touch .requirements

.package: pyproject.toml .requirements
	.venv/bin/python3 -m pip install -e .
	touch .package

$(SOURCE_PACKAGE) $(WHEEL_PACKAGE): $(wildcard src/**/*.py)
	python3 -m build

.PHONY: dist
dist: $(SOURCE_PACKAGE) $(WHEEL_PACKAGE)

.PHONY: upload_test
upload_test: $(SOURCE_PACKAGE) $(WHEEL_PACKAGE)
	python3 -m twine upload -r testpypi dist/* 

.PHONY: upload
upload: $(SOURCE_PACKAGE) $(WHEEL_PACKAGE)
	echo "Upload with twine"
	python3 -m twine upload dist/*

.PHONY: test
test: .requirements .package
	.venv/bin/python3 -m pytest

.PHONY: coverage
coverage: .requirements
	.venv/bin/python3 -m pytest --cov=trill --cov-report html


.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
	rm -rf src/trill.egg-info
	rm -f .coverage
	rm -rf htmlcov
	rm .prepped
	rm .requirements
	rm -rf .venv
	rm .package

