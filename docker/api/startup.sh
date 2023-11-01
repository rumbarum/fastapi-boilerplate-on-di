#!/bin/bash

# docker compose로 띄우는 것이 아니기 때문에, 아래 항목 필요 없음
# dockerize -wait tcp://${db}:5432 -timeout 20s

gunicorn --bind 0.0.0.0:8000 -w 4 -k uvicorn.workers.UvicornWorker application.server:app --worker-tmp-dir /dev/shm --reload
