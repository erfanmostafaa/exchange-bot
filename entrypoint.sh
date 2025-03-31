#!/bin/bash
set -e

echo "Waiting for database..."
python wait_for_db.py

# migrate 
echo "applying migrations .."
alembic upgrade head
echo "migrations applied"


echo "Starting Telegram bot..."
exec python bot.py