from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from sqlalchemy.orm import Session
import re
from decouple import config
import telegram
from datetime import datetime, timedelta
import random
import asyncio

from database import get_db
from models.user import User, Request
from handlers.menu import show_main_menu

class NewRequestHandler:
    # حالت‌های مکالمه
    (
        GET_NAME_CHOICE, GET_NEW_NAME, GET_CURRENCY, GET_COUNTRY,
        GET_TRANSACTION_TYPE, GET_PAYMENT_METHOD, GET_PRICE,
        GET_ENTITY_TYPE, GET_AMOUNT, CONFIRM_REQUEST
    ) = range(10)

    # گزینه‌های ارز
    CURRENCIES = [
        ["یورو (EUR)", "دلار آمریکا (USD)"],
        ["لیر ترکیه (TRY)", "درهم امارات (AED)"],
        ["تتر (USDT)", "پوند انگلیس (GBP)"],
        ["دلار کانادا (CAD)", "فرانک سوئیس (CHF)"],
        ["کرون سوئد (SEK)", "کرون دانمارک (DKK)"],
        ["دلار استرالیا (AUD)", "کرون نروژ (NOK)"],
        ["سایر ارزها", "❌ انصراف"]
    ]

    # گزینه‌های کشور
    EURO_COUNTRIES = [
        ["آلمان", "فرانسه", "ایتالیا"],
        ["اسپانیا", "هلند", "بلژیک"],
        ["اتریش", "پرتغال", "ایرلند"],
        ["فنلاند", "یونان", "لیتوانی"],
        ["ایران", "❌ انصراف"]
    ]

    OTHER_COUNTRIES = [
        ["آمریکا", "انگلیس", "کانادا"],
        ["ترکیه", "امارات", "سوئیس"],
        ["سوئد", "نروژ", "دانمارک"],
        ["استرالیا", "ایران", "❌ انصراف"]
    ]

    # @staticmethod
    # def generate_request_id():
    #     """تولید شناسه منحصر به فرد برای درخواست"""
    #     date_part = datetime.now().strftime("%y%m%d")
    #     random_part = random.randint(100, 999)
    #     return f"TRX-{date_part}{random_part}"

    @staticmethod
    async def start_new_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """شروع فرآیند ثبت درخواست جدید"""
        # پاکسازی کامل داده‌های قبلی
        context.user_data.clear()
        context.user_data['conversation'] = 'new_request'
        
        user_id = update.effective_user.id
        db = next(get_db())
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            await update.message.reply_text(
                "⚠️ شما ثبت‌نام نکرده‌اید. لطفاً با دستور /start ثبت‌نام کنید.",
                reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True))
            return ConversationHandler.END

        context.user_data['user_id'] = user_id
        
        keyboard = [
            ["ادامه با نام فعلی"],
            ["تغییر نام"],
            ["❌ انصراف"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"👋 سلام {user.name}!\nبرای شروع ثبت درخواست جدید لطفاً انتخاب کنید:",
            reply_markup=reply_markup
        )
        return NewRequestHandler.GET_NAME_CHOICE

    @staticmethod
    async def handle_name_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت انتخاب نام کاربر"""
        choice = update.message.text

        if choice == "❌ انصراف":
            return await NewRequestHandler.clean_cancel(update, context)
        
        if choice == "تغییر نام":
            await update.message.reply_text(
                "✏️ لطفاً نام جدید خود را وارد کنید:",
                reply_markup=ReplyKeyboardRemove()
            )
            return NewRequestHandler.GET_NEW_NAME
        
        return await NewRequestHandler.show_currency_menu(update, context)

    @staticmethod
    async def get_new_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دریافت نام جدید از کاربر"""

        new_name = update.message.text.strip()
        if len(new_name) < 3:
            await update.message.reply_text("❌ نام باید حداقل ۳ کاراکتر باشد. لطفاً مجدداً وارد کنید:")
            return NewRequestHandler.GET_NEW_NAME

        user_id = context.user_data['user_id']
        db = next(get_db())
        user = db.query(User).filter(User.user_id == user_id).first()

        if user:
            user.name = new_name
            db.commit()
            await update.message.reply_text(f"✅ نام شما به {new_name} تغییر یافت.")

        return await NewRequestHandler.show_currency_menu(update, context)

    @staticmethod
    async def show_currency_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی انتخاب ارز"""
        reply_markup = ReplyKeyboardMarkup(NewRequestHandler.CURRENCIES, resize_keyboard=True)
        await update.message.reply_text(
            "💰 لطفاً نوع ارز را انتخاب کنید:",
            reply_markup=reply_markup
        )
        return NewRequestHandler.GET_CURRENCY

    @staticmethod
    async def get_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت انتخاب ارز"""
        if update.message.text == "❌ انصراف":
            return await NewRequestHandler.clean_cancel(update, context)

        context.user_data["currency"] = update.message.text

        if "یورو" in update.message.text:
            reply_markup = ReplyKeyboardMarkup(NewRequestHandler.EURO_COUNTRIES, resize_keyboard=True)
        else:
            reply_markup = ReplyKeyboardMarkup(NewRequestHandler.OTHER_COUNTRIES, resize_keyboard=True)

        await update.message.reply_text(
            "🌍 لطفاً کشور مورد نظر را انتخاب کنید:",
            reply_markup=reply_markup
        )
        return NewRequestHandler.GET_COUNTRY

    @staticmethod
    async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت انتخاب کشور"""
        if update.message.text == "❌ انصراف":
            return await NewRequestHandler.clean_cancel(update, context)

        context.user_data["country"] = update.message.text

        keyboard = [["فروش", "خرید"], ["❌ انصراف"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "💱 لطفاً نوع تراکنش را انتخاب کنید:",
            reply_markup=reply_markup
        )
        return NewRequestHandler.GET_TRANSACTION_TYPE

    @staticmethod
    async def get_transaction_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت انتخاب نوع تراکنش"""
        if update.message.text == "❌ انصراف":
            return await NewRequestHandler.clean_cancel(update, context)

        context.user_data["transaction_type"] = update.message.text

        keyboard = [
            ["حواله بانکی", "پی پال"],
            ["اسکناس", "❌ انصراف"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "💳 لطفاً روش پرداخت را انتخاب کنید:",
            reply_markup=reply_markup
        )
        return NewRequestHandler.GET_PAYMENT_METHOD

    @staticmethod
    async def get_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت انتخاب روش پرداخت"""
        if update.message.text == "❌ انصراف":
            return await NewRequestHandler.clean_cancel(update, context)

        context.user_data["payment_method"] = update.message.text

        await update.message.reply_text(
            "💰 لطفاً قیمت پیشنهادی خود را وارد کنید:",
            reply_markup=ReplyKeyboardRemove()
        )
        return NewRequestHandler.GET_PRICE

    @staticmethod
    async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت ورود قیمت"""
        if update.message.text == "❌ انصراف":
            return await NewRequestHandler.clean_cancel(update, context)

        try:
            price = float(update.message.text.replace(",", ""))
            if price <= 0:
                raise ValueError
            context.user_data["price"] = price
        except ValueError:
            await update.message.reply_text("❌ قیمت وارد شده نامعتبر است. لطفاً یک عدد مثبت وارد کنید:")
            return NewRequestHandler.GET_PRICE

        keyboard = [["شخص", "شرکت"], ["❌ انصراف"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "👤 لطفاً نوع شخص/شرکت را انتخاب کنید:",
            reply_markup=reply_markup
        )
        return NewRequestHandler.GET_ENTITY_TYPE

    @staticmethod
    async def get_entity_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت انتخاب نوع شخص/شرکت"""
        if update.message.text == "❌ انصراف":
            return await NewRequestHandler.clean_cancel(update, context)

        context.user_data["entity_type"] = update.message.text

        keyboard = [
            ["100", "200", "300"],
            ["500", "1000", "2000"],
            ["5000", "سایر مقادیر", "❌ انصراف"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "🔢 لطفاً مقدار ارز را انتخاب کنید:",
            reply_markup=reply_markup
        )
        return NewRequestHandler.GET_AMOUNT

    @staticmethod
    async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت ورود مقدار و محاسبه نهایی"""
        if update.message.text == "❌ انصراف":
            return await NewRequestHandler.clean_cancel(update, context)

        try:
            if update.message.text == "سایر مقادیر":
                await update.message.reply_text(
                    "لطفاً مقدار مورد نظر خود را به عدد وارد کنید:",
                    reply_markup=ReplyKeyboardRemove()
                )
                return NewRequestHandler.GET_AMOUNT

            amount = int(update.message.text.replace(",", ""))
            if amount <= 0:
                await update.message.reply_text("❌ مقدار باید بزرگتر از صفر باشد")
                return NewRequestHandler.GET_AMOUNT

            price = context.user_data.get("price", 0.0)
            total = amount * price
            fee_percent = 2.5 if amount > 500 else 0.5
            fee = total * fee_percent / 100
            final_amount = total - fee

            context.user_data.update({
                "amount": amount,
                "total": total,
                "fee_percent": fee_percent,
                "fee": fee,
                "final_amount": final_amount
            })

            keyboard = [["✅ تأیید و ثبت", "❌ انصراف"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                f"🧮 محاسبات نهایی:\n\n"
                f"🔢 مقدار ارز: {amount:,}\n"
                f"💰 قیمت واحد: {price:,}\n"
                f"💵 مبلغ کل: {total:,.0f}\n"
                f"📉 کارمزد ({fee_percent}%): {fee:,.0f}\n"
                f"✅ مبلغ نهایی شما: {final_amount:,.0f}\n\n"
                f"آیا مایل به ثبت نهایی درخواست هستید؟",
                reply_markup=reply_markup
            )
            
            return NewRequestHandler.CONFIRM_REQUEST

        except ValueError:
            await update.message.reply_text("❌ مقدار وارد شده نامعتبر است. لطفاً یک عدد صحیح مثبت وارد کنید:")
            return NewRequestHandler.GET_AMOUNT

    @staticmethod
    async def confirm_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت تأیید نهایی درخواست"""
        if update.message.text == "❌ انصراف":
            return await NewRequestHandler.clean_cancel(update, context)
        
        if update.message.text == "✅ تأیید و ثبت":
            db: Session = next(get_db())
            try:
                request = Request(
                    user_id=context.user_data['user_id'],
                    currency=context.user_data['currency'],
                    transaction_type=context.user_data['transaction_type'],
                    payment_method=context.user_data['payment_method'],
                    entity_type=context.user_data['entity_type'],
                    country=context.user_data['country'],
                    amount=context.user_data['amount'],
                    price=context.user_data['price'],
                )
                
                db.add(request)
                db.commit()
                
                user = db.query(User).filter(User.user_id == context.user_data['user_id']).first()
                # success = await SendRequest.send_request_to_channel(request, user.name)
                success = True
                
                if success:
                    await update.message.reply_text(
                        f"✅ درخواست شما با موفقیت ثبت شد:\n\n"
                        f"📌 شماره درخواست: {request.id}\n"
                        f"👤 نام: {user.name}\n"
                        f"💰 ارز: {context.user_data['currency']}\n"
                        f"🌍 کشور: {context.user_data['country']}\n"
                        f"💲 قیمت واحد: {context.user_data['price']:,}\n"
                        f"🔢 مقدار: {context.user_data['amount']:,}\n"
                        f"💵 مبلغ کل: {context.user_data['total']:,.0f}\n"
                        f"📉 کارمزد ({context.user_data['fee_percent']}%): {context.user_data['fee']:,.0f}\n"
                        f"✅ مبلغ نهایی شما: {context.user_data['final_amount']:,.0f}\n"
                        f"🔄 نوع تراکنش: {context.user_data['transaction_type']}\n"
                        f"💳 روش پرداخت: {context.user_data['payment_method']}\n"
                        f"🏢 نوع: {context.user_data['entity_type']}\n\n"
                        f"از همراهی شما متشکریم!",
                        reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
                    )
                else:
                    raise Exception("خطا در ارسال درخواست به کانال")

            except Exception as e:
                db.rollback()
                print(f"Error in confirm_request: {e}")
                await update.message.reply_text(
                    f"❌ خطا در ثبت درخواست: {str(e)}\nلطفاً مجدداً تلاش کنید.",
                    reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
                )
            finally:
                context.user_data.clear()
                return ConversationHandler.END

    @staticmethod
    async def clean_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لغو عملیات با پاکسازی کامل"""
        try:
            context.user_data.clear()
            await update.message.reply_text(
                "❌ عملیات لغو شد. به منوی اصلی بازگشتید.",
                reply_markup=ReplyKeyboardRemove()
            )
            await show_main_menu(update, context)
        except Exception as e:
            print(f"Error in clean_cancel: {e}")
            await update.message.reply_text(
                "⚠️ خطا در سیستم. لطفاً مجدداً تلاش کنید.",
                reply_markup=ReplyKeyboardRemove()
            )
        finally:
            return ConversationHandler.END

    @staticmethod
    def get_conversation_handler():
        """تنظیم هندلر مکالمه برای درخواست‌های جدید"""
        return ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^📝 ثبت درخواست جدید$"), NewRequestHandler.start_new_request)],
            states={
                NewRequestHandler.GET_NAME_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, NewRequestHandler.handle_name_choice)],
                # NewRequestHandler.GET_NEW_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, NewRequestHandler.get_new_name)],
                NewRequestHandler.GET_CURRENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, NewRequestHandler.get_currency)],
                NewRequestHandler.GET_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, NewRequestHandler.get_country)],
                NewRequestHandler.GET_TRANSACTION_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, NewRequestHandler.get_transaction_type)],
                NewRequestHandler.GET_PAYMENT_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, NewRequestHandler.get_payment_method)],
                NewRequestHandler.GET_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, NewRequestHandler.get_price)],
                NewRequestHandler.GET_ENTITY_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, NewRequestHandler.get_entity_type)],
                NewRequestHandler.GET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, NewRequestHandler.get_amount)],
                NewRequestHandler.CONFIRM_REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, NewRequestHandler.confirm_request)],
            },
            fallbacks=[
                CommandHandler("cancel", NewRequestHandler.clean_cancel),
                MessageHandler(filters.Regex(r'^(❌ انصراف|انصراف|بازگشت|بازگشت به منوی اصلی|لغو)$'), NewRequestHandler.clean_cancel),
            ],
            allow_reentry=False
        )


class SendRequest:
    @staticmethod
    def escape_markdown_v2(text):
        """فرار کردن کاراکترهای خاص برای مارک‌داون تلگرام"""
        escape_chars = r'\`*_{}[]()#+-.!|~>'
        return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", str(text))

    @staticmethod
    async def send_request_to_channel(request, user_name):
        """ارسال درخواست به کانال تلگرام"""
        try:
            bot = Bot(token=config("TOKEN"))
            channel_id = config("CHANNEL_USERNAME")

            message = (
                f"📋 *درخواست جدید*\n\n"
                f"🔹 *شماره:* `{request.request_id}`\n"
                f"🔹 *نام:* {SendRequest.escape_markdown_v2(user_name)}\n"
                f"🔹 *ارز:* `{request.currency}`\n"
                f"🔹 *کشور:* `{request.country}`\n"
                f"➖➖➖➖➖➖\n"
                f"🔸 *نوع تراکنش:* `{request.transaction_type}`\n"
                f"🔸 *قیمت:* `{request.price:,}`\n"
                f"🔸 *مقدار:* `{request.amount}`\n"
                f"🔸 *روش پرداخت:* `{request.payment_method}`"
            )

            await bot.send_message(
                chat_id=channel_id,
                text=message,
                parse_mode=telegram.constants.ParseMode.MARKDOWN_V2
            )
            return True
        except Exception as e:
            print(f"⚠️ خطا در ارسال به کانال: {str(e)}")
            return False