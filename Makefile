# -------------------------------------
# MAKEFILE
# -------------------------------------


PYTHON = env/bin/python
PIP = ${PYTHON} -m pip
PIPENV = ${PYTHON} -m pipenv
PYTEST = ${PYTHON} -m pytest
FLAKE8 = ${PYTHON} -m flake8
TWINE = ${PYTHON} -mtwine

#
# commands for artifact cleanup
#

.PHONY: clean
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -type d -d -name __pycache__ -exec rm -rf {} \;


#
# commands for virtual env maintenance
#

.PHONY: reqs
reqs: reqs.lock reqs.install

.PHONY: reqs.clean
reqs.clean:
	${PIP} freeze | xargs ${PIP} uninstall -y
	${PIP} install pipenv

.PHONY: reqs.install
reqs.install:
	${PIPENV} sync --dev

.PHONY: reqs.lock
reqs.lock:
	${PIPENV} lock

.PHONY: reqs.update
reqs.update: reqs.lock reqs.install


#
# commands for testing
#

.PHONY: test
test: test.unittests test.flake8

.PHONY: test.flake8
test.flake8:
	${FLAKE8} .

.PHONY: test.unittests
test.unittests:
	${PYTEST} .


#
# commands for packaging and deploying to pypi
#

.PHONY: sdist
sdist: test
	${PYTHON} setup.py sdist

.PHONY: release
release: clean sdist
	${TWINE} upload dist/*
