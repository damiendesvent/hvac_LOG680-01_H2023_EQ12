import logging
import sys
import json
import time
import os
import requests
from signalrcore.hub_connection_builder import HubConnectionBuilder






class Main:
    def __init__(self):
        self._hub_connection = None
        self.host = os.environ["HVAC_HOST"]
        self.token = os.environ["HVAC_TOKEN"]

    def __del__(self):
        if self._hub_connection is not None:
            self._hub_connection.stop()

    def setup(self):
        self.set_sensor_hub()

    def start(self):
        self.setup()
        self._hub_connection.start()

        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

        self._hub_connection.stop()
        sys.exit(0)

    def set_sensor_hub(self):
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.host}/SensorHub?token={self.token}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )

        self._hub_connection.on(
            "ReceiveSensorData", self.on_sensor_data_received
        )
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(
                f"||| An exception was thrown closed: {data.error}"
            )
        )

    def on_sensor_data_received(self, data):
        try:
            print(data[0]["date"] + " --> " + data[0]["data"])
            date = data[0]["date"]
            date_float = float(data[0]["data"])

            self.analyze_datapoint(date, date_float)
        except ConnectionError as err:
            print(err)

    def analyze_datapoint(self, date, data):
        if data >= 80.0:
            self.send_action_to_hvac(date, "TurnOnAc", 6)
        elif data <= 20.0:
            self.send_action_to_hvac(date, "TurnOnHeater", 6)

    def send_action_to_hvac(self, date, action, nb_tick):
        request = requests.get(
            f"{self.host}/api/hvac/{self.token}/{action}/{nb_tick}", timeout=10
        )
        details = json.loads(request.text)
        print(details + "\ndate : " + date)


if __name__ == "__main__":
    main = Main()
    main.start()
