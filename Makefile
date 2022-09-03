BUILD_DIR := ./dist
VERSION := 0.0.2
PACKAGE_NAME := trill
SOURCE_PACKAGE_NAME := $(PACKAGE_NAME)-$(VERSION).tar.gz
WHEEL_PACKAGE_NAME := $(PACKAGE_NAME)-$(VERSION)-py3-none-any.whl

SOURCE_PACKAGE := $(BUILD_DIR)/$(SOURCE_PACKAGE_NAME)
WHEEL_PACKAGE := $(BUILD_DIR)/$(WHEEL_PACKAGE_NAME)


$(SOURCE_PACKAGE): dist
$(WHEEL_PACKAGE): dist

.PHONY: dist
dist: src/**/*.py
	python3 -m build


.PHONY: upload_test
upload_test: $(SOURCE_PACKAGE) $(WHEEL_PACKAGE)
	twine upload -r testpypi dist/* 

.PHONY: upload
upload: $(SOURCE_PACKAGE) $(WHEEL_PACKAGE)
	echo "Upload with twine"
	twine upload dist/*


.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
	rm -rf src/trill.egg-info
	rm -f .coverage
