#!/usr/bin/env bash

# Runs the schedule generator service

pushd "$(dirname "$0")/.."
uvicorn schedule_generator_api.main:app --reload --port 8001
popd
