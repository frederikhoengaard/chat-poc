#!/bin/bash
set -e

echo "--- black ---"
black --line-length 88 python/src/main/
black --line-length 88 python/src/test/
echo "--- isort ---"
isort python/src/main/ --multi-line 3 --profile black
isort python/src/test/ --multi-line 3 --profile black
