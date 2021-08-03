import uasyncio as asyncio
import webserver
import sensor
import logger
import set_time

try:
    loop = asyncio.get_event_loop()

    loop.create_task(set_time.update())

    loop.create_task(sensor.start_readings())

    loop.create_task(asyncio.start_server(webserver.serve, '0.0.0.0', 80))

    loop.run_forever()
except Exception as e:
    logger.log('Something went very wrong: %s' % e, write_to_log=True)
