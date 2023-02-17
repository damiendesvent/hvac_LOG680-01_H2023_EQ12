from signalrcore.hub_connection_builder import HubConnectionBuilder
import logging
import sys
import requests
import json
import time
import os
import mysql.connector as mysql
from dotenv import load_dotenv


load_dotenv()


class Main:
    def __init__(self):
        self._hub_connection = None
        self.HOST = os.getenv("HVAC_HOST",'no_host')
        self.TOKEN = os.getenv("HVAC_TOKEN",'no_token')
        self.NB_TICK = int(os.getenv("HVAC_NB_TICK",'4'))
        self.TEMP_MAX = int(os.getenv("TEMP_MAX",'18'))
        self.TEMP_MIN = int(os.getenv("TEMP_MIN",'30'))
        if self.TOKEN == 'no_token' : raise ValueError('\x1b[31m Impossible de trouver le token ! Verifiez que la variable "HVAC_TOKEN" est bien inscrite dans votre fichier .env \x1b[0m')
        if self.HOST == 'no_host' : raise ValueError('\x1b[31m Impossible de trouver l\'adresse du serveur ! Verifiez que la variable "HVAC_HOST" est bien inscrite dans votre fichier .env \x1b[0m')
    
    def __del__(self):
        if (self._hub_connection != None):
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
        self._hub_connection = HubConnectionBuilder()\
        .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")\
        .configure_logging(logging.INFO)\
        .with_automatic_reconnect({
            "type": "raw",
            "keep_alive_interval": 10,
            "reconnect_interval": 5,
            "max_attempts": 999
        }).build()

        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(lambda data: print(f"||| An exception was thrown closed: {data.error}"))

    def on_sensor_data_received(self, data):
        try:        
            print(data[0]["date"]  + " --> " + data[0]["data"])
            date = data[0]["date"]
            dp = float(data[0]["data"])

            self.analyze_datapoint(date, dp)
        except Exception as err:
            print(err)
    
    def analyze_datapoint(self, date, data):
        if (data >= self.TEMP_MAX):                
            self.send_action_to_hvac(date, "TurnOnAc", self.NB_TICKS)
        elif (data <= self.TEMP_MIN):                
            self.send_action_to_hvac(date, "TurnOnHeater", self.NB_TICKS)

    def send_action_to_hvac(self, date, action, nb_tick):
        r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{nb_tick}") 
        details = json.loads(r.text)
        print(details)


if __name__ == '__main__':
    main = Main()
    main.start()


