#!/bin/bash

export PIPENV_VERBOSITY=-1
set -e

echo "--- black ---"
pipenv run black --line-length 88 python/src/main/
pipenv run black --line-length 88 python/src/test/
echo "--- isort ---"
pipenv run isort python/src/main/ --multi-line 3 --profile black
pipenv run isort python/src/test/ --multi-line 3 --profile black
