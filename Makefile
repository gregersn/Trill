BUILD_DIR := ./dist
VERSION := 0.0.3
PACKAGE_NAME := trill
SOURCE_PACKAGE_NAME := $(PACKAGE_NAME)-$(VERSION).tar.gz
WHEEL_PACKAGE_NAME := $(PACKAGE_NAME)-$(VERSION)-py3-none-any.whl

SOURCE_PACKAGE := $(BUILD_DIR)/$(SOURCE_PACKAGE_NAME)
WHEEL_PACKAGE := $(BUILD_DIR)/$(WHEEL_PACKAGE_NAME)


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


.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
	rm -rf src/trill.egg-info
	rm -f .coverage


.prepped: requirements-dev.txt
	python3 -m venv .venv
	.venv/bin/python3 -m pip install -r requirements-dev.txt
	touch .prepped

.PHONY: init
init: .prepped

