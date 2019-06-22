.ONESHELL:
install: 
	if [ -n "$$VIRTUALENV" ]; then deactivate; fi
	pip install .

clean:
	rm -rf dist pip-wheel-metadata build
	find . -regex ".*/__pycache__" -exec rm -rf {} +
	find . -regex ".*\.egg-info" -exec rm -rf {} +

develop: requirements-devel.txt
	python -m pip install -U "pip>=18.0" "setuptools>=38.0" wheel
	python -m pip install -r requirements-devel.txt
	python -m pip install -e .

.ONESHELL:
venv: requirements-devel.txt
	python -m venv .venv
	. .venv/bin/activate
	python -m pip install -U "pip>=18.0" "setuptools>=38.0" wheel
	python -m pip install -r requirements-devel.txt
	python -m pip install -e .

.ONESHELL:
test:
	@retval=0;
	pytest --cov=connord --cov-report term-missing:skip-covered tests/
	@if [ $$? -ne 0 ]; then retval=1; fi
	@echo '============================== Test Scipts ============================='
	@for f in tests/scripts/*; do
		@echo -n "Running $$f: "
		@if ./$$f >/dev/null; then 
			@echo 'OK'
		@else
			@echo 'FAILED'
			@retval=1;
		@fi
	@done
	@echo '========================================================================'
	@exit $$retval

.ONESHELL:
tox: clean
	eval "`pyenv init -`"
	pyenv shell py37 py36
	tox

package: clean
	python setup.py sdist bdist_wheel

freeze: requirements-devel.txt
	python -m pip freeze > requirements-devel.txt

version:
	vermin connord/

version-verbose:
	vermin -vv connord/

upload: dist/*
	twine upload dist/*

test-upload: dist/*
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

test-install:
	python3 -m pip install --index-url https://test.pypi.org/simple/ connord

