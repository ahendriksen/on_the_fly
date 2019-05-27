.PHONY: clean clean-test clean-pyc clean-build docs help install_dev
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 on_the_fly tests

test: ## run tests quickly with the default Python
	python setup.py test

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source on_the_fly setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs/.nojekyll:
	mkdir -p docs
	touch docs/.nojekyll

docs: docs/.nojekyll install_dev ## generate Sphinx HTML documentation, including API docs
	rm -f doc_sources/on_the_fly.rst
	rm -f doc_sources/modules.rst
	sphinx-apidoc -o doc_sources/ on_the_fly
	make -C doc_sources clean
	make -C doc_sources html
	$(BROWSER) docs/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C doc_sources html' -R -D .

install: clean ## install the package to the active Python's site-packages
	python setup.py install

install_dev:
	# https://stackoverflow.com/a/28842733
	pip install -e .[dev]

conda_package:
	conda install conda-build -y
	conda build conda/

environment:
	conda create -y -n otf -c astra-toolbox/label/dev  -c aahendriksen -c pytorch -c conda-forge -c owlas \
		python=3.6 \
		msd_pytorch=0.5.1 \
		cudatoolkit=9.0 \
		flexdata \
		tomopy \
		dxchange \
		matplotlib \
		tqdm \
		astra-toolbox=1.9.0.dev10 \
		ipython \
		pyqtgraph \
		numexpr \
		matplotlib \
		h5py \
		pyopengl \
		pymongo \
		cone_balls=0.2.2 \
		scikit-image
	source activate otf && pip install sacred git+https://github.com/ahendriksen/sacred_utils
	source activate otf && pip install -e .
