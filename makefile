export PYTHONPATH=${PWD}/src:${PWD}
export TEST_IMAGE=pg-14.3-test

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


main:
	python main.py --env local --debug

al-rev-auto:
	alembic revision --autogenerate

al-up:
	alembic upgrade head

del-ds:
	find . -name .DS_Store -print0 | xargs rm


define check_image_and_run
    if [ -z $$(docker images -q $1) ]; then \
        echo \>\>\>\>\>\> Image $1 was not found ; \
        echo \>\>\>\>\>\> Building $1 ... ; \
        docker build -f docker/db/Dockerfile -t $1 . && \
		docker run -d -p 5432:5432 --rm $1; \
    else \
        echo \>\>\>\>\>\> Image $1 was found ; \
        echo \>\>\>\>\>\> Running $1 ... ; \
		docker run -d -p 5432:5432 --rm $1; \
    fi
endef

test-db-run:
	@echo ">>>>>> Running test db..."
	$(call check_image_and_run, $$TEST_IMAGE)

test-db-stop:
	@echo ">>>>>> Stopping test db..."
	docker ps -qf ancestor=$$TEST_IMAGE | xargs docker stop

test-db-rerun:
	@echo ">>>>>> Stop and Rerun test db..."
	make test-db-stop
	make test-db-run
