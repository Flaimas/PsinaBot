import aiosqlite

async def create_db():
    async with aiosqlite.connect('orders.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tariff TEXT,
                days INTEGER,
                status TEXT DEFAULT 'pending'
            )
        ''')
        await db.commit()

async def check_pending_order(user_id):
    async with aiosqlite.connect('orders.db') as db:
        cursor = await db.execute(
            'SELECT id FROM orders WHERE user_id = ? AND status = "pending"',
            (user_id,)
        )
        return await cursor.fetchone() # Вернет ID заказа или None

async def add_order(user_id, tariff, days):
    async with aiosqlite.connect('orders.db') as db:
        await db.execute(
            'INSERT INTO orders (user_id, tariff, days) VALUES (?, ?, ?)',
            (user_id, tariff, days)
        )
        await db.commit()

async def db_delete_user(order_id):
    async with aiosqlite.connect('orders.db') as db:
        await db.execute(
            'DELETE FROM orders WHERE id = ?',
            (order_id,)
        )
        await db.commit()

async def update_order_status(order_id: int, new_status: str):
    async with aiosqlite.connect('orders.db') as db:
        await db.execute(
            'UPDATE orders SET status = ? WHERE id = ?',
            (new_status, order_id)
        )
        await db.commit()

async def get_order(order_id):
    async with aiosqlite.connect('orders.db') as db:
        cursor = await db.execute(
            'SELECT * FROM orders WHERE id = ?',
            (order_id,)
        )
        return await cursor.fetchone()


async def get_orders_list():
    async with aiosqlite.connect('orders.db') as db:
        cursor = await db.execute(
            'SELECT id, user_id, tariff, days FROM orders WHERE status = "pending"'
        )
        return await cursor.fetchall()