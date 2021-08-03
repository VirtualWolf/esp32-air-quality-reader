import network
from ntptime import settime
import config
import logger

c = config.read_configuration()

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        logger.log('Connecting to network...')
        wlan.connect(c['ssid'], c['ssid_password'])

        while not wlan.isconnected():
            pass

    ip_address, subnet_mask, gateway, dns = wlan.ifconfig()
    logger.log('Network config: \n    IP address: %s\n    Subnet mask: %s\n    Gateway: %s\n    DNS: %s' % (ip_address, subnet_mask, gateway, dns))

connect_to_wifi()

settime()
