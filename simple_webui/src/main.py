from aerospacejam import AerospaceJamServer
import time

WIFI_CONFIG = {
    'ssid': 'CHANGEME_AerospaceJam', # You should change these two lines!
    'password': 'CHANGEME_password',
    'static_ip': '192.168.4.1',
    'subnet_mask': '255.255.255.0',
    'gateway': '192.168.4.1',
    'dns': '192.168.4.1'
}

# Initialize the server with your Wi-Fi configuration
pico_server = AerospaceJamServer(WIFI_CONFIG)

# Register a sensor - this is a dummy sensor
pico_server.register_sensor("dummy", lambda: 25 + (time.time() % 10))

# Start the web server
pico_server.run()

