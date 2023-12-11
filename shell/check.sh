#!/bin/bash
set -e

echo "--- black ---"
black --line-length 88 --check python/src/main/
black --line-length 88 --check python/src/test/
echo "--- isort ---"
isort python/src/main/ --multi-line 3 --profile black --check
isort python/src/test/ --multi-line 3 --profile black --check
echo "--- flake8 ---"
flake8 python/src/main/
flake8 python/src/test/
echo "--- pytest ---"
if [[ "$OSTYPE" == "msys" ]]; then
   PYTHONPATH="./python/src/main;$PYTHONPATH" pytest python/src/test/
 else
   PYTHONPATH=./python/src/main:$PYTHONPATH pytest python/src/test/
 fi
