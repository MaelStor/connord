.ONESHELL:
install: connord/scripts/openvpn_up_down.bash
	install -Dm750 connord/scripts/openvpn_up_down.bash \
		/etc/openvpn/client/openvpn_up_down.bash
	install -Dm750 connord/scripts/openvpn_up_down.bash \
		/var/openvpn/etc/openvpn/client/openvpn_up_down.bash
	if [ -n "$$VIRTUALENV" ]; then deactivate; fi
	pip install .

clean:
	rm -rf dist pip-wheel-metadata
	find . -regex ".*/__pycache__" -exec rm -rf {} +
	find . -regex ".*\.egg-info" -exec rm -rf {} +

.ONESHELL:
develop: requirements-devel.txt
	virtualenv .venv
	. .venv/bin/activate
	python -m pip install -U "pip>=18.0" "setuptools>=38.0" wheel
	python -m pip install -r requirements-devel.txt
	python -m pip install -e .

test:
	pytest --cov=connord --cov-report term-missing:skip-covered tests/

package: clean
	python setup.py sdist bdist_wheel

freeze: requirements-devel.txt
	python -m pip freeze > requirements-devel.txt

version:
	vermin connord/

version-verbose:
	vermin -vv connord/

test-upload: dist/*
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

test-install:
	python3 -m pip install --index-url https://test.pypi.org/simple/ connord

