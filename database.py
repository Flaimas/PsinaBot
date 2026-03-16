import aiosqlite
from config import DB_PATH

async def create_db():
    async with get_db() as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tariff TEXT,
                days INTEGER,
                status TEXT DEFAULT 'pending'
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

async def get_db():
    return aiosqlite.connect(DB_PATH)

async def check_notification(user_id):
    async with get_db() as db:
        cursor = await db.execute(
            'SELECT user_id FROM notifications WHERE notification = 0 AND user_id = ?',
            (user_id,)
        )
        return await cursor.fetchone()

async def set_notified(user_id, notification):
    async with get_db() as db:
        await db.execute(
            'INSERT OR REPLACE INTO notifications (user_id, notification) VALUES (?, ?)',
            (user_id, notification)
        )
        await db.commit()

async def check_pending_order(user_id):
    async with get_db() as db:
        cursor = await db.execute(
            'SELECT id FROM orders WHERE user_id = ? AND status = "pending"',
            (user_id,)
        )
        return await cursor.fetchone() # Вернет ID заказа или None

async def check_extend_order(user_id):
    async with get_db() as db:
        cursor = await db.execute(
            'SELECT id FROM orders WHERE user_id = ? AND status = "extend"',
            (user_id,)
        )
        return await cursor.fetchone() # Вернет ID заказа или None

async def check_order(user_id, status):
    async with get_db() as db:
        cursor = await db.execute(
            'SELECT id FROM orders WHERE user_id = ? AND status = ?',
            (user_id, status)
        )
        return await cursor.fetchone() # Вернет ID заказа или None

async def add_order(user_id, tariff, days):
    async with get_db() as db:
        await db.execute(
            'INSERT INTO orders (user_id, tariff, days) VALUES (?, ?, ?)',
            (user_id, tariff, days)
        )
        await db.commit()

async def add_expire_order(user_id, tariff, days, status):
    async with get_db() as db:
        await db.execute(
            'INSERT INTO orders (user_id, tariff, days, status) VALUES (?, ?, ?, ?)',
            (user_id, tariff, days, status)
        )
        await db.commit()

async def db_delete_user(order_id):
    async with get_db() as db:
        await db.execute(
            'DELETE FROM orders WHERE id = ?',
            (order_id,)
        )
        await db.commit()

async def update_order_status(order_id: int, new_status: str):
    async with get_db() as db:
        await db.execute(
            'UPDATE orders SET status = ? WHERE id = ?',
            (new_status, order_id)
        )
        await db.commit()

async def get_order(order_id):
    async with get_db() as db:
        cursor = await db.execute(
            'SELECT * FROM orders WHERE id = ?',
            (order_id,)
        )
        return await cursor.fetchone()


async def get_orders_list(status):
    async with get_db() as db:
        cursor = await db.execute(
            'SELECT id, user_id, tariff, days FROM orders WHERE status = ?',
            (status,)
        )
        return await cursor.fetchall()

