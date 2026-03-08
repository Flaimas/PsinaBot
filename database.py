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

async def add_order(user_id, tariff, days):
    async with aiosqlite.connect('orders.db') as db:
        await db.execute(
            'INSERT INTO orders (user_id, tariff, days) VALUES (?, ?, ?)',
            (user_id, tariff, days)
        )
        await db.commit()

async def get_order(order_id):
    async with aiosqlite.connect('orders.db') as db:
        cursor = await db.execute(
            'SELECT * FROM orders WHERE id = ?',
            (order_id,)
        )
        return await cursor.fetchone()