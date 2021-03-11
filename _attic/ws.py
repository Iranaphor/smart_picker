
from websocket import create_connection
import threading
import time
import json

class WS(threading.Thread):
    def __init__(self, address="wss://lcas.lincoln.ac.uk/car/ws", user_name="picker02", update_orders_cb=None):
        threading.Thread.__init__(self)
        self._ws = create_connection(address)
        self.user_name = user_name
        self.update_orders_cb = update_orders_cb
        self.stop_event = threading.Event()

    def call_robot(self):
        self._ws.send(json.dumps({'method':'call', 'user': self.user_name}))

    def cancel_robot(self):
        self._ws.send(json.dumps({'method':'cancel', 'user': self.user_name}))

    def set_loaded(self):
        self._ws.send(json.dumps({'method':'set_state', 'user': self.user_name, 'state': 'LOADED'}))

    def set_init(self):
        self._ws.send(json.dumps({'method':'set_state', 'user': self.user_name, 'state': 'INIT'}))

    def send_gps(self, lat, lon, epx, epy, ts=time.time()):
        self._ws.send(json.dumps(
            {
                'method':'location_update', 
                'row':'3', 
                'user': self.user_name, 
                'latitude':float(lat), 
                'longitude':float(lon), 
                'accuracy':float(epx), 
                'rcv_time':ts
            }
        ))

    def run(self):
        while not self.stop_event.is_set():
            msg = json.loads(self._ws.recv()) #< blocking

            if msg['method'] == 'update_orders' and self.user_name in msg['states']:
                # call update_orders callback
                if self.update_orders_cb is not None:
                    self.update_orders_cb(msg['states'][self.user_name])

        self._ws.close()

    def stop(self):
        self.stop_event.set()