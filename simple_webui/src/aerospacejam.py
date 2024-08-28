import network
import socket

def capitalize_first_letter(s: str) -> str:
    """
    Capitalizes the first letter of the passed string and returns it.
    """
    if not s:
        return s  # Return the empty string if input is empty
    return s[0].upper() + s[1:].lower()

class AerospaceJamServer:
    """
    A barebones realtime WebUI implementation for the Aerospace Jam.
    """
    def __init__(self, config: dict):
        """
        Initializes the server and starts the Wi-Fi AP.
        
        Args:
        - config: a dictionary containing AP settings.
        """
        self.config = config
        self.sensors = {}
        self.ap = None
        self.template = self.load_template('webui.html')
        
        self.start_wifi_ap()

    def start_wifi_ap(self):
        """
        Starts a Wi-Fi AP with the config stored in obj.config.
        """
        self.ap = network.WLAN(network.AP_IF)
        self.ap.config(essid=self.config['ssid'], password=self.config['password'])
        self.ap.ifconfig((self.config['static_ip'], self.config['subnet_mask'], self.config['gateway'], self.config['dns']))
        self.ap.active(True)
        print(f"Hotspot {self.config['ssid']} started with IP: {self.config['static_ip']}")

    def register_sensor(self, name, read_function):
        """
        Registers a sensor to the WebUI.
        
        Args:
        - name: The name of the sensor, displayed in the WebUI.
        - read_function: The function that is called when the sensor is read from - should return an object that can be converted to a string.
        """
        self.sensors[name] = read_function

    def load_template(self, template_path):
        """
        Loads a template from a given filesystem path.
        """
        with open(template_path, 'r') as file:
            return file.read()

    def generate_web_page(self, sensor_values):
        """
        Generates the WebUI from a template.
        """
        sensor_data_html = ""
        update_js = ""

        for name, value in sensor_values.items():
            sensor_name = capitalize_first_letter(name)
            sensor_data_html += f'<p>{sensor_name}: <span id="{name}">{value}</span></p>\n'
            update_js += f'document.getElementById("{name}").innerText = data.{name};\n'

        return self.template.format(sensor_data_html=sensor_data_html, update_js=update_js)

    def handle_client(self, conn):
        """
        Handles an open connection from a client - a single web request.
        """
        request = conn.recv(1024)
        request = str(request)
        
        if '/sensors' in request:
            sensor_data = {name: read_func() for name, read_func in self.sensors.items()}
            response = str(sensor_data).replace("'", '"')  # Convert to JSON
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
        else:
            sensor_data = {name: read_func() for name, read_func in self.sensors.items()}
            response = self.generate_web_page(sensor_data)
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
        
        conn.close()

    def run(self):
        """
        Runs the server, blocks until an error or an interrupt.
        """
        addr = socket.getaddrinfo(self.config['static_ip'], 80)[0][-1]
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse the address
        s.bind(addr)
        s.listen(1)
        
        print(f'Web server running on http://{self.config["static_ip"]}/')

        try:
            while True:
                conn, addr = s.accept()
                print('Got a request from %s' % str(addr))
                self.handle_client(conn)
        finally:
            s.close()

