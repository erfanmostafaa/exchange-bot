#!/usr/bin/env python

import argparse
from bot import main as run_bot

def migrate_database():
    print("Running database migrations...")

def start_bot():
    print("Starting the Telegram bot...")
    run_bot()

def main():
    parser = argparse.ArgumentParser(description="Manage the Telegram bot.")
    parser.add_argument(
        "command",
        choices=["start", "migrate"],
        help="Command to run: 'start' to run the bot, 'migrate' to run database migrations.",
    )
    args = parser.parse_args()

    if args.command == "start":
        start_bot()
    elif args.command == 'migrate':
        migrate_database()
    else:
        print("Invalid command. Use 'start' or 'migrate'.")

if __name__ == "__main__":
    main()