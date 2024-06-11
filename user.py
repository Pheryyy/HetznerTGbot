from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import hetzner_api
import payment
import config

# State definitions for ConversationHandler
SELECT_PLAN, CONFIRM_PURCHASE, CHARGE_AMOUNT = range(3)

plans = {
    "CAX11": {"ram": 4, "cpu": 2, "disk": 40, "type": "CAX"},
    "CAX21": {"ram": 8, "cpu": 4, "disk": 80, "type": "CAX"},
    "CAX31": {"ram": 16, "cpu": 8, "disk": 160, "type": "CAX"},
    "CPX11": {"ram": 2, "cpu": 2, "disk": 40, "type": "CPX"},
    "CPX21": {"ram": 4, "cpu": 3, "disk": 80, "type": "CPX"},
    "CPX31": {"ram": 8, "cpu": 4, "disk": 160, "type": "CPX"},
    "CX22": {"ram": 4, "cpu": 2, "disk": 40, "type": "CX"},
    "CX32": {"ram": 8, "cpu": 4, "disk": 80, "type": "CX"},
    "CX42": {"ram": 16, "cpu": 8, "disk": 160, "type": "CX"},
    "CX11": {"ram": 2, "cpu": 1, "disk": 20, "type": "CX"},
    "CX21": {"ram": 4, "cpu": 2, "disk": 40, "type": "CX"},
    "CX31": {"ram": 8, "cpu": 2, "disk": 80, "type": "CX"},
}

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id == config.ADMIN_USER_ID:
        await update.message.reply_text(f'سلام {config.ADMIN_NAME}!')
    else:
        await update.message.reply_text('سلام! برای خرید سرور، دستور /buy را وارد کنید.')

async def buy(update: Update, context: CallbackContext) -> None:
    keyboard = []
    for plan, specs in plans.items():
        keyboard.append([InlineKeyboardButton(f"{plan} > RAM {specs['ram']}|CPU {specs['cpu']}|Disk {specs['disk']}GB", callback_data=plan)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('لطفا پلن مورد نظر خود را با توجه به مشخصات زیر انتخاب کنید:', reply_markup=reply_markup)
    return SELECT_PLAN

async def select_plan(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    selected_plan = query.data
    context.user_data['selected_plan'] = selected_plan
    specs = plans[selected_plan]
    
    await query.edit_message_text(text=f"پلن انتخاب شده:\n{selected_plan} > RAM {specs['ram']}|CPU {specs['cpu']}|Disk {specs['disk']}GB\nآیا تأیید می‌کنید؟ (بله/خیر)")
    return CONFIRM_PURCHASE

async def confirm_purchase(update: Update, context: CallbackContext) -> None:
    confirmation = update.message.text
    if confirmation.lower() == 'بله':
        user_id = update.message.from_user.id
        selected_plan = context.user_data['selected_plan']
        specs = plans[selected_plan]
        cost = hetzner_api.calculate_cost(specs)
        if payment.charge(user_id, cost):
            server_info = hetzner_api.create_server(specs)
            await update.message.reply_text(f'سرور با موفقیت ساخته شد:\n{server_info}')
        else:
            await update.message.reply_text('موجودی کیف پول شما کافی نیست. لطفاً کیف پول خود را شارژ کنید.')
    else:
        await update.message.reply_text('خرید لغو شد.')
    return ConversationHandler.END

async def check_balance(update: Update, context: CallbackContext) -> None:
    balance = payment.get_balance(update.message.from_user.id)
    await update.message.reply_text(f'موجودی شما: {balance} تومان')

async def list_servers(update: Update, context: CallbackContext) -> None:
    servers = hetzner_api.get_user_servers(update.message.from_user.id)
    if not servers:
        await update.message.reply_text('شما هیچ سروری ندارید.')
        return
    server_list = '\n'.join([f"{server['name']}: {server['id']}" for server in servers])
    await update.message.reply_text(f'لیست سرورهای شما:\n{server_list}')

async def contact_support(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('برای تماس با پشتیبانی، پیام خود را ارسال کنید.')

async def charge_wallet(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('لطفاً مبلغی که می‌خواهید کیف پول خود را شارژ کنید وارد کنید:')
    return CHARGE_AMOUNT

async def process_charge(update: Update, context: CallbackContext) -> None:
    amount = int(update.message.text)
    user_id = update.message.from_user.id
    payment.process_payment(user_id, amount)
    await update.message.reply_text(f'کیف پول شما به مبلغ {amount} تومان شارژ شد.')
    return ConversationHandler.END

# مدیریت سرورها
async def create_server(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('لطفاً مشخصات سرور جدید را وارد کنید.')

async def rebuild_server(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('لطفاً ID سرور مورد نظر برای بازسازی را وارد کنید.')

async def reset_server(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('لطفاً ID سرور مورد نظر برای ریست را وارد کنید.')

async def reboot_server(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('لطفاً ID سرور مورد نظر برای ریبوت را وارد کنید.')

# Conversation handler for purchase process
purchase_handler = ConversationHandler(
    entry_points=[CommandHandler('buy', buy)],
    states={
        SELECT_PLAN: [CallbackQueryHandler(select_plan)],
        CONFIRM_PURCHASE: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_purchase)],
    },
    fallbacks=[]
)
