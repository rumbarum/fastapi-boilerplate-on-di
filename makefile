export PYTHONPATH=${PWD}/src:${PWD}

lint:
	black src/
	isort src/

format:
	make lint
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place src/ --exclude=__init__.py

my:
	mypy src/
blc:
	black --check src/
isc:
	isort src -c


run:
	python main.py --env local --debug

al-rev:
	alembic revision --autogenerate

al-up:
	alembic upgrade head

del-ds:
	find . -name .DS_Store -print0 | xargs rm
