import requests
import config

def get_servers():
    response = requests.get('https://api.hetzner.cloud/v1/servers', headers={'Authorization': f'Bearer {config.HETZNER_API_KEY}'})
    return response.json()

def get_limits():
    response = requests.get('https://api.hetzner.cloud/v1/account', headers={'Authorization': f'Bearer {config.HETZNER_API_KEY}'})
    return response.json()['account']['limits']

def get_user_servers(user_id):
    # این تابع نیاز به پیاده‌سازی بیشتر دارد تا سرورهای کاربر را برگرداند
    return []

def calculate_cost(specs):
    # محاسبه هزینه براساس مشخصات سرور
    return specs['cpu'] * 10 + specs['ram'] * 5 + specs['disk'] * 0.1  # فرمول فرضی

def create_server(specs):
    data = {
        "name": "server-name",
        "server_type": specs['type'],
        "image": "ubuntu-20.04",
        "location": "fsn1",
        "start_after_create": True,
    }
    response = requests.post('https://api.hetzner.cloud/v1/servers', headers={'Authorization': f'Bearer {config.HETZNER_API_KEY}'}, json=data)
    return response.json()

def get_all_user_ids():
    # تابع برای بازگرداندن تمامی شناسه‌های کاربران
    return [user_id for user_id in user_balances.keys()]
