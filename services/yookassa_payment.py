import uuid
import aiohttp
import base64

class YooKassaClient:
    def __init__(self, account_id: str, secret_key: str, url: str = 'https://api.yookassa.ru/v3/payments'):
        self.url = url

        auth_string = f'{account_id}:{secret_key}'
        auth_encoded = base64.b64encode(auth_string.encode()).decode()

        self.headers = {
            'Authorization': f'Basic {auth_encoded}',
            'Content-Type': 'application/json'
        }

        self._session: aiohttp.ClientSession | None=None

    async def get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self.headers)
        return self._session

    async def close_session(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def find_one(self, payment_id: str):
        session = await self.get_session()
        try:
            async with session.get(f"{self.url}/{payment_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    print(f"Ошибка при получении платежа: {payment_id}. Статус: {response.status}")
                    return None
        except Exception as e:
            print(f'Ошибка сети при поиске платежа: {e}')


    async def create(self, data: dict, idempotence_key: str):
        headers = {
            'Idempotence-Key': idempotence_key
        }
        session = await self.get_session()
        try:
            async with session.post(self.url, headers=headers, json=data) as response:
                response_data = await response.json()

                if response.status in (200, 201):
                    return response_data

                print(f'Ошибка при создании платежа: Статус: {response.status}. Ответ: {response_data}')
                return None

        except Exception as e:
            print(f"Ошибка при создании платежа: {e}")
