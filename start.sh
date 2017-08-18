#!/bin/bash
gunicorn --reload --error-logfile error.log --capture-output -D -b 127.0.0.1:8001 -p bot.pid run:app
