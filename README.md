# esp32-air-quality-reader

An application to read data from a [Plantower PMS5003](http://plantower.com/en/content/?108.html) air quality sensor, written for use with [MicroPython on an ESP32 microcontroller](https://micropython.org). It has a webserver to return the data in JSON format, and `/html` can be hit to return a pretty(ish) HTML version.

The sensor data extraction code is based on Adafruit's [old Python code](https://learn.adafruit.com/pm25-air-quality-sensor/python-and-circuitpython) from before they turned it into [a library](https://github.com/adafruit/Adafruit_CircuitPython_PM25/blob/main/adafruit_pm25/__init__.py).

## Helpful tools
* [micropy-cli](https://github.com/BradenM/micropy-cli)
* [Pymakr](https://marketplace.visualstudio.com/items?itemName=pycom.Pymakr)

## Setup
It requires a file called `config.json` at the root of the `src` directory, configured with your wifi network name and password, the RX pin that the PMS5003 sensor is connected to, and an API key that protects the `POST` and `DELETE` endpoints described below. An example file is given in [config.example.json](src/config.example.json).

## Endpoints
esp32-air-quality-reader has five HTTP endpoints:
* `GET /` — Get the current air quality values in JSON format.
* `GET /html` — Get the current air quality values in HTML format.
* `GET /log` — View the log file that's written to when errors occur.
* `DELETE /log` — Clear the log file; this requires the `X-API-Key` header to be set with the same value as what you're sending to the endpoint.
* `POST /reset` — Restarts the ESP32; as above, it requires the `X-API-Key` header to be set.
