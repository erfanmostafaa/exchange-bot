#!/bin/bash
set -e

echo "Waiting for database..."
python database.py

# migrate 
echo "applying migrations .."
alembic upgrade head
echo "migrations applied"


echo "Starting Telegram bot..."
exec python bot.py