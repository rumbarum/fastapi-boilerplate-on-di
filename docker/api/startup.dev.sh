#!/bin/bash
dockerize -wait tcp://db:5432 -timeout 20s

alembic upgrade head && uvicorn --host 0.0.0.0 application.server:app --reload
