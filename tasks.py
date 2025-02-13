async def send_reminder(bot, user_id, text):
    await bot.send_message(user_id, text) 