.PHONY: install build install-dev build-dev

install:
	pip install ./website-generator

install-dev:
	pip install -e ./website-generator

build:
	python website-generator/src/website_generator/ --hash "$(shell git log --pretty=format:'%h' -n 1)"

build-dev: build
	watchmedo shell-command --recursive --drop \
		-c 'python website-generator/src/website_generator/ --hash DevMode' \
		./pages ./templates ./public ./website-generator

all: install build
