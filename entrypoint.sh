#!/bin/bash
set -e 

echo "Waiting for database..."
python wait_for_db.py 

echo "Database is available!/"

echo "Running database migrations..."
python manage.py migrate  

echo "Starting the bot..."
python manage.py start  
