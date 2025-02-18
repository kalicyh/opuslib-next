# Makefile for opuslib.
#
# Author:: kalicyh <kalicyh@qq.com>
# Copyright:: Copyright (c) 2025, Kalicyh
# License:: BSD 3-Clause License
#


.DEFAULT_GOAL := all


all: develop

develop:
	python setup.py develop

install:
	python setup.py install

install_requirements_test:
	pip install -r requirements_test.txt

uninstall:
	pip uninstall -y opuslib

reinstall: uninstall develop

remember_test:
	@echo
	@echo "Hello from the Makefile..."
	@echo "Don't forget to run: 'make install_requirements_test'"
	@echo

clean:
	rm -rf *.egg* build dist *.py[oc] */*.py[co] cover doctest_pypi.cfg \
		nosetests.xml pylint.log *.egg output.xml flake8.log tests.log \
		test-result.xml htmlcov fab.log *.deb .coverage

publish:
	python setup.py sdist
	twine upload dist/*

nosetests: remember_test
	python setup.py nosetests

flake8: pep8

pep8: remember_test
	flake8 --ignore=E402,E731 --max-complexity 12 --exit-zero opuslib/*.py \
	opuslib/api/*.py tests/*.py

pylint: lint

lint: remember_test
	pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
	-r n opuslib/*.py opuslib/api/*.py tests/*.py || exit 0

test: lint pep8 mypy nosetests

mypy:
	mypy --strict .

docker_build:
	docker build .

checkmetadata:
	python setup.py check -s --metadata --restructuredtext
