.PHONY: format

PWD := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

format:
	pre-commit run --all-files
