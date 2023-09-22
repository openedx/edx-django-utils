# Base Makefile components to build on.
#
# Ideally, this would be pulled in from another repo by a `git subtree`
# reference and would include most of the Makefile so that upgrading
# repos to the latest functionality (and keeping them standardized)
# would be fast and simple.

PYTHON_VER := 3.8

# These are required for bootstrapping a virtualenv to the point where
# requirements can be installed.

VENV := .venv-$(PYTHON_VER)
PIP := $(VENV)/bin/pip
PIP-COMPILE := $(VENV)/bin/pip-compile
PIP-SYNC := $(VENV)/bin/pip-sync

$(VENV): ## Create the virtualenv, or recreate it if it already exists
	python$(PYTHON_VER) -m venv $(VENV) --clear

$(PIP): $(VENV)
	pip install -r requirements/pip.txt

$(PIP-COMPILE) $(PIP-SYNC): $(VENV)
	$(PIP) install -r requirements/pip-tools.txt

# The rest of the Python tools are listed here, and all are fulfilled
# by the same target. By calling them from their explicit virtualenv
# paths, we ensure that the virtualenv will be used (including by
# other tools they call).

COVERAGE := $(VENV)/bin/coverage
DIFF-COVER := $(VENV)/bin/diff-cover
PYTEST := $(VENV)/bin/pytest
TOX := $(VENV)/bin/tox

$(VENV)/bin/%: $(VENV)
	make requirements
