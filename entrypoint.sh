#!/bin/bash
set -e

echo "Waiting for database..."
python wait_for_db.py

echo "Running database migrations..."
if [ -f "alembic.ini" ]; then
  alembic upgrade head
else
  python -c "
from database import Base, engine
from models.user import User  # تمام مدل‌های خود را import کنید
Base.metadata.create_all(bind=engine)
print('Database tables created successfully.')
"
fi

echo "Starting Telegram bot..."
exec python bot.py