#!/bin/bash
set -e

echo "Starting SSH ..."
service ssh start

exec python /app/manage.py process_tasks &