from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import config
import hetzner_api
import payment

async def admin_panel(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != config.ADMIN_USER_ID:
        await update.message.reply_text('شما دسترسی لازم برای استفاده از این فرمان را ندارید.')
        return

    keyboard = [
        [InlineKeyboardButton("مشاهده آمار", callback_data='stats')],
        [InlineKeyboardButton("تعداد تراکنش‌ها", callback_data='transactions')],
        [InlineKeyboardButton("تعداد سرورها و اطلاعات آنها", callback_data='servers_info')],
        [InlineKeyboardButton("ارسال پیام همگانی", callback_data='announce')],
        [InlineKeyboardButton("ارسال پیام به یک فرد", callback_data='message_user')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('به پنل ادمین خوش آمدید! یک گزینه را انتخاب کنید:', reply_markup=reply_markup)

async def handle_admin_callbacks(update: Update, context: CallbackContext) -> None:
    if update.callback_query.from_user.id != config.ADMIN_USER_ID:
        await update.callback_query.answer('شما دسترسی لازم برای استفاده از این فرمان را ندارید.')
        return

    query = update.callback_query
    data = query.data

    if data == 'stats':
        await show_stats(query)
    elif data == 'transactions':
        await show_transactions(query)
    elif data == 'servers_info':
        await show_servers_info(query)
    elif data == 'announce':
        await query.message.reply_text('لطفاً پیام همگانی خود را ارسال کنید:')
        context.user_data['awaiting_announcement'] = True
    elif data == 'message_user':
        await query.message.reply_text('لطفاً شناسه کاربری و پیام را به صورت "USER_ID:MESSAGE" ارسال کنید:')
        context.user_data['awaiting_user_message'] = True

async def show_stats(query) -> None:
    limits = hetzner_api.get_limits()
    servers = hetzner_api.get_servers()
    stats_message = f"آمار:\nسرورها: {len(servers['servers'])}\nمحدودیت‌ها: {limits}"
    await query.message.reply_text(stats_message)

async def show_transactions(query) -> None:
    transactions = payment.get_all_transactions()
    await query.message.reply_text(f'تعداد تراکنش‌ها: {len(transactions)}')

async def show_servers_info(query) -> None:
    servers = hetzner_api.get_servers()
    server_list = '\n'.join([f"{server['name']} (ID: {server['id']})" for server in servers['servers']])
    await query.message.reply_text(f'تعداد سرورها: {len(servers["servers"])}\nاطلاعات سرورها:\n{server_list}')

async def announce(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != config.ADMIN_USER_ID:
        await update.message.reply_text('شما دسترسی لازم برای استفاده از این فرمان را ندارید.')
        return

    message = update.message.text
    users = get_all_user_ids()
    for user_id in users:
        await context.bot.send_message(chat_id=user_id, text=message)
    await update.message.reply_text('پیام همگانی ارسال شد.')

async def message_user(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != config.ADMIN_USER_ID:
        await update.message.reply_text('شما دسترسی لازم برای استفاده از این فرمان را ندارید.')
        return

    data = update.message.text.split(':')
    if len(data) != 2:
        await update.message.reply_text('فرمت پیام نادرست است. لطفاً به صورت "USER_ID:MESSAGE" ارسال کنید.')
        return

    user_id, message = data
    await context.bot.send_message(chat_id=user_id, text=message)
    await update.message.reply_text('پیام ارسال شد.')

# افزودن هندلرهای مربوط به انتظار پیام
async def handle_message(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('awaiting_announcement'):
        await announce(update, context)
        context.user_data['awaiting_announcement'] = False
    elif context.user_data.get('awaiting_user_message'):
        await message_user(update, context)
        context.user_data['awaiting_user_message'] = False

