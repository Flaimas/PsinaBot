import aiohttp
from config import MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD
from datetime import datetime, timedelta, timezone
import time

class MarzbanAPI:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.session = None
        self.token = None

    async def _request(self, method, url, **kwargs):
        api_session = await self._get_session()
        headers = {'Authorization': f'Bearer {self.token}'}
        kwargs['headers'] = headers

        async with getattr(api_session, method)(url, **kwargs) as r:
            if r.status == 401:
                await self.get_token()
                kwargs['headers'] = {'Authorization': f'Bearer {self.token}'}
                async with getattr(api_session, method)(url, **kwargs) as r2:
                    return r2.status, await r2.json()
            return r.status, await r.json()

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def get_token(self):
        api_session = await self._get_session()
        payload = {'username': self.username, 'password': self.password}
        async with api_session.post(f'{self.url}/api/admin/token', data=payload) as r:
            data = await r.json()
            self.token = data['access_token']
            return data['access_token']

    async def get_user_link(self, username):
        status, data = await self._request('get', f'{self.url}/api/user/{username}')
        if status == 200:
            return ''.join(data['links'])
        return f"Error: {status}!"

    async def create_user(self, username: str, days: int, tariff: str, data_limit: int = 214748364800,
                          status: str = "active", data_limit_reset_strategy: str = "month"):

        utc_days = self.get_expire_timestamp(days)
        data = {
            'username': username,
            'expire': utc_days,
            'data_limit': data_limit,
            'status': status,
            "data_limit_reset_strategy": data_limit_reset_strategy,
            'note': tariff,
            'proxies': {
                'vless': {
                    'flow': 'xtls-rprx-vision'
                }
            },
            'inbounds': {
                'vless': [
                    'VLESS TCP REALITY',
                    'VLESS TCP TLS',
                ]
            }
        }
        resp_status, data = await self._request('post', f'{self.url}/api/user', json=data)
        return resp_status == 200

    async def delete_user(self, username):
        status, data = await self._request('delete', f'{self.url}/api/user/{username}')
        if status == 200:
            return True
        return False

    async def get_user_info(self, username: str):
        status, data = await self._request('get', f'{self.url}/api/user/{username}')
        if status == 200:
            return data
        return None

    async def get_all_user(self):
        status, data = await self._request('get', f'{self.url}/api/users')
        if status == 200:
            return data
        return None

    async def update_user(self, username: str, expire: int, data_limit: int, tariff: str,
                          reset_strategy: str = 'month'):
        payload = {
            "expire": expire,
            "data_limit": data_limit,
            "data_limit_reset_strategy": reset_strategy,
            "note": tariff,
        }
        status, data = await self._request('put', f'{self.url}/api/user/{username}', json=payload)
        return status == 200
    
    async def update_subscription(self, username: str, tariff: str, expire_now: int,
                                  day: int, reset_traffic: bool = False):
        payload = {
            "expire": expire_now + int(timedelta(days=day).total_seconds()),
            "note": tariff
        }
        status, data = await self._request('put', f'{self.url}/api/user/{username}', json=payload)

        if reset_traffic:
            await self.reset_user_traffic(username=username)

        return status == 200
    
    async def add_next_plan(self, username: str, tariff: str, expire_now: int, day: int):
        NEXT_TARIF_EXPIRE = expire_now + int(timedelta(days=day).total_seconds())
        NEXT_TARIF_DATA_LIMIT = 214748364800
        payload = {
            "next_plan": {
                "add_remaining_traffic": False,
                "data_limit": NEXT_TARIF_DATA_LIMIT,
                "expire": NEXT_TARIF_EXPIRE,
                "fire_on_either": True
            },
            "note": tariff
        }
        status, data = await self._request('put', f'{self.url}/api/user/{username}', json=payload)
        return status == 200

    async def reset_user_traffic(self, username: str):
        status, data = await self._request('post', f'{self.url}/api/user/{username}/reset')
        return status == 200

    async def update_referrer_sub(self, tg_id: int):
        username = f'tg_{tg_id}'
        user_data = await self.get_user_info(username)

        if not user_data:
            return False

        expire = user_data.get('expire')
        now_ts = int(datetime.now(timezone.utc).timestamp())
        DAYS_7 = 7 * 24 * 60 * 60

        if expire:
            start_point = max(expire, now_ts)
            user_data['expire'] = int(start_point + DAYS_7)
        else:
            return False
        status, data = await self._request('put', f'{self.url}/api/user/{username}', json=user_data)
        return status == 200

    async def close(self):
        if self.session:
            await self.session.close()

    @staticmethod
    def get_expire_timestamp(days: int) -> int:
        expire = datetime.now(timezone.utc) + timedelta(days=days)
        return int(expire.timestamp())