all:
	tox

lint:
	tox -e flake8,pylint,mypy

test:
	tox -e test
