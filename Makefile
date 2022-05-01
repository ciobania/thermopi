.PHONY: build clean test install

install-deps:
	@python3 -m pip install --upgrade pip
	#@pip install poetry
	#@poetry install

build:
	@python3 setup.py sdist bdist_wheel

build-install: # also installs it locally
	@python3 setup.py sdist bdist_wheel
	@python3 setup.py install --user

clean:
	@rm -rf build dist
	@python3 -m pip uninstall thermopi

test:
	@pytest tests