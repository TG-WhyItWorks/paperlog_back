#!/bin/bash

echo "Detecting model changes and creating migration"
alembic revision --autogenerate -m "$1" # bash에서 bash scripts/migrate.sh "update ~ table" 입력

echo "Applying migration to database"
alembic upgrade head

echo "Migration completed"