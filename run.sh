#!/bin/bash

# start flask server
gunicorn flasksite:app "$@" \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --workers 1 \
    --worker-class gthread
