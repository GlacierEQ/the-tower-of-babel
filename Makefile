.PHONY: generate check test

generate:
	python tools/generate.py

check:
	python tools/generate.py --check

test: check
	python -m unittest discover -s tests -v
