from config import MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD
import requests
from datetime import datetime, timedelta, timezone

def get_expire_timestamp(days: int) -> int:
    expire = datetime.now(timezone.utc) + timedelta(days=days)
    return int(expire.timestamp())

def get_token():
    r = requests.post(f'{MARZBAN_URL}/api/admin/token', data={
        'username': MARZBAN_USERNAME,
        'password': MARZBAN_PASSWORD
    })
    return r.json()['access_token']

def get_user_link(username):
    r = requests.get(f'{MARZBAN_URL}/api/user/{username}', headers={'Authorization': f'Bearer {get_token()}'})
    return r.json()['links']

def create_user(username, days):
    token = get_token()
    utc_days = get_expire_timestamp(days)
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'username': username,
        'expire': utc_days,
        'proxies': {
            'vless': {
                'flow': 'xtls-rprx-vision'
            }
        },
        'inbounds': {
            'vless': ['VLESS TCP TLS']
        }
    }
    r = requests.post(f'{MARZBAN_URL}/api/user', json=data, headers=headers)

def delete_user(username):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.delete(f'{MARZBAN_URL}/api/user/{username}', headers=headers)
    print(r.json())

def check_user(username):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f'{MARZBAN_URL}/api/user/{username}', headers=headers)
    if r.status_code == 200:
        return True
    else:
        return False

check_user('Test')