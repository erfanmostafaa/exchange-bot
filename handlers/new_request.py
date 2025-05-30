from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, CommandHandler
from database import get_db
from models.user import User, Request
from decouple import config
from sqlalchemy.orm import Session
import telegram
import re
from datetime import datetime
import random

class NewRequestHandler:
    GET_NAME_CHOICE, GET_NEW_NAME, GET_CURRENCY, GET_TRANSACTION_TYPE, GET_PAYMENT_METHOD, GET_ENTITY_TYPE, GET_COUNTRY, GET_AMOUNT, GET_PRICE = range(9)

    @staticmethod
    async def start_new_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        db = next(get_db())

        user = db.query(User).filter(User.user_id == user_id).first()

        if user:
            context.user_data['name'] = user.name
            keyboard = [
                [InlineKeyboardButton("تغییر نام", callback_data="change_name")],
                [InlineKeyboardButton("انصراف", callback_data="cancel_request")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"نام شما اکنون در سیستم {user.name} ثبت شده است. آیا می‌خواهید نام خود را تغییر دهید؟",
                reply_markup=reply_markup,
            )
            return NewRequestHandler.GET_NAME_CHOICE
        else:
            await update.message.reply_text("شما ثبت‌نام نکرده‌اید. لطفاً ابتدا ثبت‌نام کنید.")
            return ConversationHandler.END

    @staticmethod
    async def handle_name_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "change_name":
            await query.edit_message_text("لطفاً نام جدید خود را وارد کنید:")
            return NewRequestHandler.GET_NEW_NAME
        elif query.data == "cancel_request":
            return await NewRequestHandler.cancel_request(update, context)

    @staticmethod
    async def get_new_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_name = update.message.text
        user_id = update.effective_user.id

        db = next(get_db())
        user = db.query(User).filter(User.user_id == user_id).first()

        if user:
            user.name = user_name
            db.commit()
            context.user_data['name'] = user_name
            await update.message.reply_text(f"نام شما به {user_name} تغییر یافت.")
        else:
            await update.message.reply_text("کاربر یافت نشد.")
            return ConversationHandler.END

        keyboard = [
            [InlineKeyboardButton("دلار", callback_data="USD")],
            [InlineKeyboardButton("یورو", callback_data="EUR")],
            [InlineKeyboardButton("تتر", callback_data="USDT")],
            [InlineKeyboardButton("درهم", callback_data="AED")],
            [InlineKeyboardButton("دلار کانادا", callback_data="CAD")],
            [InlineKeyboardButton("انصراف", callback_data="cancel_request")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("لطفاً نوع ارز را انتخاب کنید:", reply_markup=reply_markup)
        return NewRequestHandler.GET_CURRENCY

    @staticmethod
    async def get_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "cancel_request":
            return await NewRequestHandler.cancel_request(update, context)

        context.user_data["currency"] = query.data

        keyboard = [
            [InlineKeyboardButton("فروش", callback_data="sell")],
            [InlineKeyboardButton("خرید", callback_data="buy")],
            [InlineKeyboardButton("انصراف", callback_data="cancel_request")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("لطفاً نوع تراکنش را انتخاب کنید:", reply_markup=reply_markup)
        return NewRequestHandler.GET_TRANSACTION_TYPE

    @staticmethod
    async def get_transaction_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "cancel_request":
            return await NewRequestHandler.cancel_request(update, context)

        context.user_data["transaction_type"] = query.data

        keyboard = [
            [InlineKeyboardButton("حواله بانکی", callback_data="bank_transfer")],
            [InlineKeyboardButton("پی پال", callback_data="paypal")],
            [InlineKeyboardButton("اسکناس", callback_data="cash")],
            [InlineKeyboardButton("انصراف", callback_data="cancel_request")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("لطفاً روش پرداخت را انتخاب کنید:", reply_markup=reply_markup)
        return NewRequestHandler.GET_PAYMENT_METHOD

    @staticmethod
    async def get_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "cancel_request":
            return await NewRequestHandler.cancel_request(update, context)

        context.user_data["payment_method"] = query.data

        await query.edit_message_text("لطفاً قیمت پیشنهادی خود را وارد کنید:")
        return NewRequestHandler.GET_PRICE

    @staticmethod
    async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            price = float(update.message.text)
            context.user_data["price"] = price
        except ValueError:
            await update.message.reply_text("قیمت وارد شده نامعتبر است. لطفاً یک عدد وارد کنید.")
            return NewRequestHandler.GET_PRICE

        keyboard = [
            [InlineKeyboardButton("شخص", callback_data="individual")],
            [InlineKeyboardButton("شرکت", callback_data="company")],
            [InlineKeyboardButton("انصراف", callback_data="cancel_request")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("لطفاً نوع شخص/شرکت را انتخاب کنید:", reply_markup=reply_markup)
        return NewRequestHandler.GET_ENTITY_TYPE

    @staticmethod
    async def get_entity_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "cancel_request":
            return await NewRequestHandler.cancel_request(update, context)

        context.user_data["entity_type"] = query.data

        keyboard = [
            [InlineKeyboardButton("آمریکا", callback_data="USA")],
            [InlineKeyboardButton("هلند", callback_data="Netherlands")],
            [InlineKeyboardButton("آلمان", callback_data="Germany")],
            [InlineKeyboardButton("کانادا", callback_data="Canada")],
            [InlineKeyboardButton("ایران", callback_data="Iran")],
            [InlineKeyboardButton("انصراف", callback_data="cancel_request")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("لطفاً کشور را انتخاب کنید:", reply_markup=reply_markup)
        return NewRequestHandler.GET_COUNTRY

    @staticmethod
    async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "cancel_request":
            return await NewRequestHandler.cancel_request(update, context)

        context.user_data["country"] = query.data

        keyboard = [
            [InlineKeyboardButton("100", callback_data="100")],
            [InlineKeyboardButton("200", callback_data="200")],
            [InlineKeyboardButton("300", callback_data="300")],
            [InlineKeyboardButton("400", callback_data="400")],
            [InlineKeyboardButton("500", callback_data="500")],
            [InlineKeyboardButton("1000", callback_data="1000")],
            [InlineKeyboardButton("2000", callback_data="2000")],
            [InlineKeyboardButton("3000", callback_data="3000")],
            [InlineKeyboardButton("4000", callback_data="4000")],
            [InlineKeyboardButton("5000", callback_data="5000")],
            [InlineKeyboardButton("انصراف", callback_data="cancel_request")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("لطفاً مقدار ارز را انتخاب کنید:", reply_markup=reply_markup)
        return NewRequestHandler.GET_AMOUNT

    @staticmethod
    def generate_request_id():
        """تولید شماره درخواست منحصر به فرد"""
        date_part = datetime.now().strftime("%y%m%d")
        random_part = random.randint(100, 999)
        return f"TRX-{date_part}{random_part}"

    @staticmethod
    async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "cancel_request":
            return await NewRequestHandler.cancel_request(update, context)

        context.user_data["amount"] = query.data

        db: Session = next(get_db())

        request = Request(
            user_id=update.effective_user.id,
            name=context.user_data['name'],
            currency=context.user_data['currency'],
            transaction_type=context.user_data['transaction_type'],
            price=context.user_data["price"],
            payment_method=context.user_data['payment_method'],
            entity_type=context.user_data['entity_type'],
            country=context.user_data['country'],
            amount=context.user_data['amount']
        )
        db.add(request)
        db.commit()
        db.refresh(request)

        await SendRequest.send_request_to_channel(request)

        await query.edit_message_text(
            f"درخواست شما ثبت شد\n\n"
            f"➤ نام: {context.user_data['name']}\n"
            f"➤ ارز: {context.user_data['currency']}\n"
            f"➤ نوع تراکنش: {context.user_data['transaction_type']}\n"
            f"➤ قیمت پیشنهادی: {context.user_data['price']}\n"
            f"➤ روش پرداخت: {context.user_data['payment_method']}\n"
            f"➤ شخص/شرکت: {context.user_data['entity_type']}\n"
            f"➤ کشور: {context.user_data['country']}\n"
            f"➤ مقدار ارز: {context.user_data['amount']}"
        )

        context.user_data.clear()
        return ConversationHandler.END

    @staticmethod
    async def cancel_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        await query.edit_message_text("عملیات لغو شد. به منوی اصلی بازگشتید.")
        from handlers.menu_handler import show_main_menu
        await show_main_menu(update, context)

        context.user_data.clear()
        return ConversationHandler.END

    @staticmethod
    def get_conversation_handler():
        return ConversationHandler(
            entry_points=[CommandHandler("new_request", NewRequestHandler.start_new_request)],
            states={
                NewRequestHandler.GET_NAME_CHOICE: [CallbackQueryHandler(NewRequestHandler.handle_name_choice)],
                NewRequestHandler.GET_NEW_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, NewRequestHandler.get_new_name)],
                NewRequestHandler.GET_CURRENCY: [CallbackQueryHandler(NewRequestHandler.get_currency)],
                NewRequestHandler.GET_TRANSACTION_TYPE: [CallbackQueryHandler(NewRequestHandler.get_transaction_type)],
                NewRequestHandler.GET_PAYMENT_METHOD: [CallbackQueryHandler(NewRequestHandler.get_payment_method)],
                NewRequestHandler.GET_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, NewRequestHandler.get_price)],
                NewRequestHandler.GET_ENTITY_TYPE: [CallbackQueryHandler(NewRequestHandler.get_entity_type)],
                NewRequestHandler.GET_COUNTRY: [CallbackQueryHandler(NewRequestHandler.get_country)],
                NewRequestHandler.GET_AMOUNT: [CallbackQueryHandler(NewRequestHandler.get_amount)],
            },
            fallbacks=[CommandHandler("cancel", NewRequestHandler.cancel_request)],
        )


class SendRequest:
    @staticmethod
    def escape_markdown_v2(text):
        """Escape special characters for Telegram MarkdownV2"""
        escape_chars = r'\`*_{}[]()#+-.!|~>'
        return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", str(text))

    @staticmethod
    async def send_request_to_channel(request):
        bot = Bot(token=config("TOKEN"))

        try:
            message = (
                f"📋 *درخواست جدید*\n\n"
                f"🔹 *شماره:* `{request.id}`\n"
                f"🔹 *نام:* {SendRequest.escape_markdown_v2(request.name)}\n"
                f"🔹 *ارز:* `{request.currency}`\n"
                f"🔹 *نوع تراکنش:* `{request.transaction_type}`\n"
                f"🔹 *قیمت پیشنهادی:* `{request.price}`\n"
                f"🔹 *روش پرداخت:* `{request.payment_method}`\n"
                f"🔹 *شخص/شرکت:* `{request.entity_type}`\n"
                f"🔹 *کشور:* `{request.country}`\n"
                f"🔹 *مقدار ارز:* `{request.amount}`"
            )

            await bot.send_message(
                chat_id=config("CHANNEL_USERNAME"),
                text=message,
                parse_mode=telegram.constants.ParseMode.MARKDOWN_V2
            )
        except Exception as e:
            print(f"⚠️ خطا در ارسال درخواست به کانال: {e}")