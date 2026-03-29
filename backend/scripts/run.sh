#!/usr/bin/env bash

# Runs the backend

pushd "$(dirname "$0")/.."
uvicorn core_api.main:app --reload --port 8000
popd
