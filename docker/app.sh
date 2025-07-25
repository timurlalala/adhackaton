#!/bin/bash

sleep 2 # Wait for the database to be ready

alembic revision --autogenerate -m "initial_setup"
alembic upgrade head

sleep 1

cd src || exit

#gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
uvicorn main_webapp:app --host=0.0.0.0 --port=8000