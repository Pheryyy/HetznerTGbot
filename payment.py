user_balances = {}
all_transactions = []

def process_payment(user_id, amount):
    if user_id in user_balances:
        user_balances[user_id] += amount
    else:
        user_balances[user_id] = amount
    all_transactions.append({'user_id': user_id, 'amount': amount})

def get_balance(user_id):
    return user_balances.get(user_id, 0)

def charge(user_id, amount):
    if user_id in user_balances and user_balances[user_id] >= amount:
        user_balances[user_id] -= amount
        return True
    return False

def process_online_payment(user_id, amount):
    # پیاده‌سازی فرایند پرداخت آنلاین با استفاده از API درگاه پرداخت
    response = requests.post(config.PAYMENT_API_URL, json={'user_id': user_id, 'amount': amount})
    return response.json()

def get_all_transactions():
    return all_transactions
