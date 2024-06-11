from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import logging
import config
import admin
import user
import os

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("/etc/telegram-hetzner-bot/bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main() -> None:
    application = Application.builder().token(config.API_TOKEN).build()

    application.add_handler(CommandHandler("start", user.start))
    application.add_handler(CommandHandler("admin", admin.admin_panel))
    application.add_handler(CallbackQueryHandler(admin.handle_admin_callbacks))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, admin.handle_message))
    application.add_handler(user.purchase_handler)  # افزودن کنورسیشن هندلر برای فرآیند خرید
    application.add_handler(CommandHandler("balance", user.check_balance))
    application.add_handler(CommandHandler("servers", user.list_servers))
    application.add_handler(CommandHandler("support", user.contact_support))
    application.add_handler(CommandHandler("create_server", user.create_server))
    application.add_handler(CommandHandler("rebuild_server", user.rebuild_server))
    application.add_handler(CommandHandler("reset_server", user.reset_server))
    application.add_handler(CommandHandler("reboot_server", user.reboot_server))
    application.add_handler(CommandHandler("charge", user.charge_wallet))

    # استفاده از وب‌هوک
    WEBHOOK_URL = 'https://bot.netbrain.fun/telegram-webhook'
    port = 8443
    logger.info(f"Setting webhook at {WEBHOOK_URL} on port {port}")
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=config.API_TOKEN,
        webhook_url=WEBHOOK_URL
    )

if __name__ == '__main__':
    logger.info("Starting bot")
    main()
