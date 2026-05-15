import aiosqlite
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
                reward_balance INTEGER DEFAULT 0,
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
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tg_id INTEGER NOT NULL,
                        amount REAL NOT NULL,
                        tariff_name TEXT NOT NULL,
                        day INTEGER NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending',
                        payment_id TEXT UNIQUE,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        paid_at DATETIME
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

async def get_referrer(tg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            'SELECT referrer_id FROM users WHERE tg_id = ?',
            (tg_id,)
        ) as cursor:
            referrer_id = await cursor.fetchone()
            return referrer_id[0] if referrer_id else None

async def get_count_referrals(referrer_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE referrer_id = ?",
            (referrer_id,)
        ) as cursor:
            count_ref = await cursor.fetchone()
            return count_ref[0] if count_ref else None

async def get_reward_balance(tg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT reward_balance FROM users WHERE tg_id = ?",
            (tg_id,)
        ) as cursor:
            reward_balance = await cursor.fetchone()
            return reward_balance[0] if reward_balance else None

async def add_reward(reward: int, tg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET reward_balance = reward_balance + ? WHERE tg_id = ?",
            (reward, tg_id)
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

async def create_transaction(tg_id: int, amount: float, tariff_name: str, day: int, payment_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO transactions (tg_id, amount, tariff_name, day, payment_id)'
            'VALUES (?, ?, ?, ?, ?)', (tg_id, amount, tariff_name, day, payment_id)
        )
        await db.commit()

async def get_active_transaction(tg_id: int, tariff_name: str, day: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT payment_id, created_at FROM transactions '
            'WHERE tg_id = ? AND tariff_name = ? AND day = ? AND status = "pending" '
            'ORDER BY created_at DESC LIMIT 1',
            (tg_id, tariff_name, day)
        )
        return await cursor.fetchone()

async def get_order_info(payment_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT tg_id, tariff_name, day, status FROM transactions '
            'WHERE payment_id = ?',
            (payment_id,)
        )
        return await cursor.fetchone()

async def succeeded_transaction(payment_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT tg_id, tariff_name, day, status FROM transactions '
            'WHERE payment_id = ?', (payment_id,)
        )

        row = await cursor.fetchone()
        if row and row[3] == 'pending':
            tg_id, tariff_name, day = row[0], row[1], row[2]

            await db.execute(
                'UPDATE transactions SET status = "succeeded", paid_at = CURRENT_TIMESTAMP '
                'WHERE payment_id = ?', (payment_id,)
            )
            await db.commit()

            return tg_id, tariff_name, day

        return None

async def issued_subscription(payment_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE transactions SET status = 'issued' WHERE payment_id = ?",
            (payment_id,)
        )
        await db.commit()