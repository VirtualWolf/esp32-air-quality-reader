import uasyncio as asyncio
from ntptime import settime
import utime
import logger

async def update():
    while True:
        logger.log('Updating time from NTP server')
        settime()

        # Sleep for 24 hours
        await asyncio.sleep(86400)
