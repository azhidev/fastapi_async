import asyncio, time

async def task():
    while True:
        print(time.time())
        await asyncio.sleep(3)