# Base Makefile components to build on.
#
# Ideally, this would be pulled in from another repo by a `git subtree`
# reference and would include most of the Makefile so that upgrading
# repos to the latest functionality (and keeping them standardized)
# would be fast and simple.

PYTHON_VER := 3.8

# These are required for bootstrapping a virtualenv to the point where
# requirements can be installed.

venv_name := .venv-$(PYTHON_VER)
pip := $(venv_name)/bin/pip
pip-compile := $(venv_name)/bin/pip-compile
pip-sync := $(venv_name)/bin/pip-sync

$(venv_name): ## Create the virtualenv, or recreate it if it already exists
	python$(PYTHON_VER) -m venv $(venv_name) --clear

$(pip): $(venv_name)
	pip install -r requirements/pip.txt

$(pip-compile) $(pip-sync): $(venv_name)
	$(pip) install -r requirements/pip-tools.txt

# The rest of the Python tools are listed here, and all are fulfilled
# by the same target. By calling them from their explicit virtualenv
# paths, we ensure that the virtualenv will be used (including by
# other tools they call).

coverage := $(venv_name)/bin/coverage
diff-cover := $(venv_name)/bin/diff-cover
pytest := $(venv_name)/bin/pytest
tox := $(venv_name)/bin/tox

$(venv_name)/bin/%: $(venv_name)
	make requirements
