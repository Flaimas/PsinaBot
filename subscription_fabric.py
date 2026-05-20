from loader import marzban_api

async def change_subscription(username: str, new_tariff: str, day: int):
    user_data = await marzban_api.get_user_info(username=username)
    if user_data:
        tariff, expire_now = user_data['note'], user_data['expire']

        if tariff == new_tariff:
            if await marzban_api.update_subscription(username=username, tariff=new_tariff, expire_now=expire_now, day=day):
                return True
        
        if tariff != new_tariff:
            if await marzban_api.add_next_plan(username=username, tariff=new_tariff, expire_now=expire_now, day=day):
                return True
            
        return False
    return False