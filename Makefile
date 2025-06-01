SHELL := /bin/bash

.PHONY: all black test integration-test build clean push format setup

all: test

black:
	black .

format:
	pre-commit run --all-files

setup:
	./setup.sh

test:
	tox

integration-test:
	tox -e integration

build:
	python3 -m build

clean:
	rm dist/ build/ -rfv

push:
	python3 -m twine upload --repository fear-and-greed --repository-url=https://upload.pypi.org/legacy/ --skip-existing dist/*
