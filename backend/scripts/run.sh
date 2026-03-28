#!/usr/bin/env bash

# Runs the backend

pushd "$(dirname "$0")/.."
uvicorn app.main:app --reload --port 8000
popd
