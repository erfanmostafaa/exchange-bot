# تنظیمات پایه
CHANNEL_USERNAME = "@arzinoexchannel"

# انواع حواله‌ها
TRANSFER_TYPES = {
    "transfer": "حواله بانکی",
    "paypal": "پی پال",
    "cash": "اسکناس"
}

# الگوی regex برای استخراج اطلاعات از پیام‌ها
TRANSFER_REGEX = r"""
    (?P<country>[\w\s]+)\s+
    (?P<amount>[\d,]+)\s+
    مبلغ\s+(?P<value>[\d,]+)\s+
    نرخ\s*:(?P<price>\d+)\s+
    حواله
"""