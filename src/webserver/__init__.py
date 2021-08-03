import os
import gc
import re
import ujson
import uasyncio as asyncio
import machine
import sensor
import logger
import config

c = config.read_configuration()

async def get_log(writer):
    # Full credit to https://github.com/marcidy/micropython-uasyncio-webexample for this!
    file_stat = os.stat('log')
    file_size = file_stat[6]

    writer.write(b'HTTP/1.1 200 OK\r\n')
    writer.write(b'Content-Type: text/plain\r\n')
    writer.write(b'Content-Length: %s\r\n' % file_size)
    writer.write(b'Accept-Ranges: none\r\n')
    writer.write(b'Transfer-Encoding: chunked\r\n')
    writer.write(b'Connection: close\r\n')
    writer.write(b'\r\n')

    await writer.drain()
    gc.collect()

    max_chunk_size = 1024

    with open('log') as file:
        for x in range(0, file_size, max_chunk_size):
            chunk_size = min(max_chunk_size, file_size - x)
            chunk_header = "{:x}\r\n".format(chunk_size).encode('utf-8')
            writer.write(chunk_header)
            writer.write(file.read(chunk_size))
            writer.write(b'\r\n')
            await writer.drain()
            gc.collect()

    writer.write(b"0\r\n")
    writer.write(b"\r\n")

    await writer.drain()
    writer.close()
    await writer.wait_closed()

    gc.collect()

async def clear_log(writer, is_authorised_request):
    if (is_authorised_request):
        with open('log', 'w'):
            pass

        logger.log('Log file cleared', write_to_log=True)
        await send_response(writer, 'Log file cleared!', 'text/plain')
    else:
        await send_403(writer)

async def get_queue(writer):
    queue = '\n'.join(os.listdir('queue'))
    await send_response(writer, queue, 'text/plain')

async def clear_queue(writer, is_authorised_request):
    if is_authorised_request:
        queue = os.listdir('queue')

        for file in queue:
            logger.log('Removing %s...' % file)
            os.remove('queue/%s' % file)

        await send_response(writer, 'Queue cleared', 'text/plain')
    else:
        await send_403(writer)

async def reset_board(writer, is_authorised_request):
    if is_authorised_request:
        logger.log('Board reset requested', write_to_log=True)
        await send_response(writer, 'Resetting board...', 'text/plain')
        await asyncio.sleep(2)

        machine.reset()
    else:
        await send_403(writer)

async def generate_html(writer):
    content = (
        '<html>\n'
        '<head><title>ESP32 Air Quality Sensor</title></head>\n'
        '<body>\n'
        '<h1>PM<sub>1.0</sub>: {pm_1_0}</h1>\n'
        '<h1>PM<sub>2.5</sub>: {pm_2_5}</h1>\n'
        '<h1>PM<sub>10</sub>: {pm_10}</h1>\n'
        '<ul>\n'
        '<li>Particles > 0.3&#181;m / 0.1L air &mdash; {particles_0_3um}</li>\n'
        '<li>Particles > 0.5&#181;m / 0.1L air &mdash; {particles_0_5um}</li>\n'
        '<li>Particles > 1.0&#181;m / 0.1L air &mdash; {particles_1_0um}</li>\n'
        '<li>Particles > 2.5&#181;m / 0.1L air &mdash; {particles_2_5um}</li>\n'
        '<li>Particles > 5.0&#181;m / 0.1L air &mdash; {particles_5_0um}</li>\n'
        '<li>Particles > 10&#181;m / 0.1L air &mdash; {particles_10um}</li>\n'
        '</ul>\n'
        '</body>\n'
        '</html>'
        .format(**sensor.get_current_data())
        )

    await send_response(writer, content, 'text/html')

async def send_response(writer, content, content_type, response_code='200 OK'):
    writer.write(b'HTTP/1.1 %s\r\n' % response_code)

    if content_type != '':
        writer.write(b'Content-Type: %s\r\n' % content_type)

    writer.write(b'Connection: close\r\n')
    writer.write(b'\r\n')

    if content != '':
        writer.write(b'%s\r\n' % content)

    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def send_403(writer):
    await send_response(writer, '403 Forbidden', 'text/plain', '403 FORBIDDEN')

async def serve(reader, writer):
    req = await reader.readline()

    is_authorised_request = False

    while True:
        h = await reader.readline()

        if 'X-API-Key: %s\r\n' % c['api_key'] in h:
            is_authorised_request = True

        if h in (b'', b'\r\n'):
            break

    if 'POST /reset' in req:
        await reset_board(writer, is_authorised_request)
    elif 'GET /log ' in req:
        await get_log(writer)
    elif 'DELETE /log ' in req:
        await clear_log(writer, is_authorised_request)
    elif 'GET /html ' in req:
        await generate_html(writer)
    elif 'GET / ' in req:
        await send_response(writer, ujson.dumps(sensor.get_current_data()), 'application/json')
    else:
        await send_response(writer, 'Resource not found', 'text/plain', '404 NOT FOUND')

    gc.collect()
