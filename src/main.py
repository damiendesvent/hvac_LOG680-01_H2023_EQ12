import logging
import sys
import time
import os
import requests
from signalrcore.hub_connection_builder import HubConnectionBuilder
from dotenv import load_dotenv


load_dotenv()  # lecture du fichier .env


class Main:
    def __init__(self):
        self._hub_connection = None
        # on importe les variables d'environnement :
        self.host = os.getenv("HVAC_HOST", "no_host")

        self.token = os.getenv("HVAC_TOKEN", "no_token")
        self.nb_ticks = int(os.getenv("HVAC_NB_TICK", "4"))

        self.temps_max = int(os.getenv("TEMP_MAX", "24"))
        self.temps_min = int(os.getenv("TEMP_MIN", "18"))

        # on stoppe le programme si on ne trouve pas les variables :
        if self.token == "no_token":
            raise ValueError(
                '\x1b[31m Impossible de trouver le token ! Verifiez que la variable "HVAC_TOKEN" est bien inscrite dans votre fichier .env \x1b[0m'
            )
        if self.host == "no_host":
            raise ValueError(
                '\x1b[31m Impossible de trouver l\'adresse du serveur ! Verifiez que la variable "HVAC_HOST" est bien inscrite dans votre fichier .env \x1b[0m'
            )

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
            data = float(data[0]["data"])

            self.analyze_datapoint(date, data)
        except ConnectionError as err:
            print(err)

    def analyze_datapoint(self, date, data):
        if data >= self.temps_max:
            self.send_action_to_hvac("TurnOnAc", self.nb_ticks)
        elif data <= self.temps_min:
            self.send_action_to_hvac("TurnOnHeater", self.nb_ticks)

    def send_action_to_hvac(self, action, nb_tick):
        response = requests.get(
            f"{self.host}/api/hvac/{self.token}/{action}/{nb_tick}"
        )
        details = response.json()
        print(details)


if __name__ == "__main__":
    main = Main()
    main.start()
