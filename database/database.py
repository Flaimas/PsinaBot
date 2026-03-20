import aiosqlite
from pydantic import with_config

from config import DB_PATH

async def create_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER PRIMARY KEY,
                username TEXT,
                referrer_id INTEGER,
                trial_used INTEGER DEFAULT 0,
                balance INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME,
                is_banned INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                user_id INTEGER UNIQUE,
                notification INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
                    CREATE TABLE IF NOT EXISTS trials (
                        user_id INTEGER UNIQUE
                    )
                ''')
        await db.commit()

async def check_or_register_user(tg_id: int, username: str = None,
                                 referrer_id: int = None):
    """
        Пытается создать юзера. Если он есть — обновляет время захода.
        Возвращает True, если юзер был создан только что (новый).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        res = await db.execute(
            "SELECT 1 FROM users WHERE tg_id = ?", (tg_id, )
        )
        exist = await res.fetchone()
        if not exist:
            query = """
            INSERT INTO users (tg_id, username, referrer_id, last_activity)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """
            await db.execute(query, (tg_id, username, referrer_id))
            await db.commit()
            return True #юзер новый
        await db.execute(
            "UPDATE users SET last_activity = CURRENT_TIMESTAMP, username = ? WHERE tg_id = ?",
            (username, tg_id)
        )
        await db.commit()
        return False #юзер старый

async def check_use_trial(tg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        res = await db.execute(
            "SELECT trial_used FROM users WHERE tg_id = ?",
            (tg_id,)
        )
        used = await res.fetchone()
        used = used[0] if used else None
        return bool(used)

async def set_trial_used(tg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET trial_used = 1 WHERE tg_id = ?",
            (tg_id,)
        )
        await db.commit()


async def check_notification(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT user_id FROM notifications WHERE notification = 0 AND user_id = ?',
            (user_id,)
        )
        return await cursor.fetchone()

async def set_notified(user_id, notification):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT OR REPLACE INTO notifications (user_id, notification) VALUES (?, ?)',
            (user_id, notification)
        )
        await db.commit()

async def check_pending_order(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT id FROM orders WHERE user_id = ? AND status = "pending"',
            (user_id,)
        )
        return await cursor.fetchone() # Вернет ID заказа или None

async def check_extend_order(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT id FROM orders WHERE user_id = ? AND status = "extend"',
            (user_id,)
        )
        return await cursor.fetchone() # Вернет ID заказа или None

async def check_order(user_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT id FROM orders WHERE user_id = ? AND status = ?',
            (user_id, status)
        )
        return await cursor.fetchone() # Вернет ID заказа или None

async def add_order(user_id, tariff, days):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO orders (user_id, tariff, days) VALUES (?, ?, ?)',
            (user_id, tariff, days)
        )
        await db.commit()

async def add_expire_order(user_id, tariff, days, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO orders (user_id, tariff, days, status) VALUES (?, ?, ?, ?)',
            (user_id, tariff, days, status)
        )
        await db.commit()

async def db_delete_user(order_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'DELETE FROM orders WHERE id = ?',
            (order_id,)
        )
        await db.commit()

async def update_order_status(order_id: int, new_status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE orders SET status = ? WHERE id = ?',
            (new_status, order_id)
        )
        await db.commit()

async def get_order(order_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT * FROM orders WHERE id = ?',
            (order_id,)
        )
        return await cursor.fetchone()


async def get_orders_list(status):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT id, user_id, tariff, days FROM orders WHERE status = ?',
            (status,)
        )
        return await cursor.fetchall()