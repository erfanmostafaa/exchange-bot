from telegram.ext import Application
from decouple import config
from handlers.setup_handler import setup_all_handlers

def main():
    app = Application.builder().token(config("TOKEN")).build()

    setup_all_handlers(app)

    app.run_polling()

if __name__ == "__main__":
    main()