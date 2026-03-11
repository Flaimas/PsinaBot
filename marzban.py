import aiohttp
from config import MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD
from datetime import datetime, timedelta, timezone
from prices import PRICES


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

    async def create_user(self, username, days, tariff, data_limit = 214748364800):
        utc_days = self.get_expire_timestamp(days)
        data = {
            'username': username,
            'expire': utc_days,
            'data_limit': data_limit,
            "data_limit_reset_strategy": "month",
            'note': tariff,
            'proxies': {
                'vless': {
                    'flow': 'xtls-rprx-vision'
                }
            },
            'inbounds': {
                'vless': ['VLESS TCP TLS']
            }
        }
        status, data = await self._request('post', f'{self.url}/api/user', json=data)
        if status == 200:
            return True
        else:
            return False

    async def delete_user(self, username):
        status, data = await self._request('delete', f'{self.url}/api/user/{username}')
        if status == 200:
            return True
        return False

    async def check_user(self, username):
        status, data = await self._request('get', f'{self.url}/api/user/{username}')
        if status == 200:
            return True
        else:
            return False

    async def get_user_info(self, username):
        status, data = await self._request('get', f'{self.url}/api/user/{username}')
        if status == 200:
            return data
        return None

    async def update_user(self, username: str, expire: int, data_limit: int, data_limit_reset_strategy: str = 'month'):
        json_data = {
            "expire": expire,
            "data_limit": data_limit,
            "data_limit_reset_strategy": data_limit_reset_strategy
        }
        status, data = await self._request('put', f'{self.url}/api/user/{username}', json=json_data)
        return status == 200

    async def close(self):
        if self.session:
            await self.session.close()

    @staticmethod
    def get_expire_timestamp(days: int) -> int:
        expire = datetime.now(timezone.utc) + timedelta(days=days)
        return int(expire.timestamp())

marzban_api = MarzbanAPI(MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD)