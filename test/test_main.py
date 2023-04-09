import os
import unittest
import sys
import io
from unittest.mock import patch
import datetime
from dotenv import load_dotenv
import requests
from src.main import Main
from src.db import SessionLocal
from src.utils import get_temperature_by_date

load_dotenv()

HOST = os.getenv("HVAC_HOST", "no_host")
TOKEN = os.getenv("HVAC_TOKEN", "no_token")
NB_TICKS = int(os.getenv("HVAC_NB_TICK", "4"))
TEMP_MAX = int(os.getenv("TEMP_MAX", "24"))
TEMP_MIN = int(os.getenv("TEMP_MIN", "18"))


class TestMain(unittest.TestCase):
    def setUp(self):
        self.main = Main()

    def tearDown(self):
        self.main.Base.metadata.drop_all(self.main.engine)

    def test_simulator_up(self):
        response = requests.get(f"{HOST}/api/health")
        self.assertEqual("All system operational Commander !", response.text)

    @patch("requests.get")
    def test_turn_on_ac(self, mock_get):
        # Variables
        action = "TurnOnAc"
        data = [
            {"date": str(datetime.datetime.now()), "data": str(TEMP_MAX + 1.0)}
        ]

        # Mocked responses
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response.json = lambda: {
            "Response": "Activating AC for " + str(NB_TICKS) + " ticks"
        }

        # Setup our resquest get mocked (the next request.get will receive our mocked response)
        mock_get.return_value = mock_response

        # Redirect stdout to a temporary buffer (To catch printed lines)
        stdout_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = stdout_buffer

        # Run the code we want to test
        # main = Main()
        self.main.on_sensor_data_received(data)

        # Check that the get request's methode use the correct http URL
        mock_get.assert_called_once_with(
            f"{HOST}/api/hvac/{TOKEN}/{action}/{NB_TICKS}"
        )

        # Get all printed lines during execution
        sys.stdout = old_stdout
        printed_lines = stdout_buffer.getvalue().splitlines()

        # Check printed data
        self.assertEqual(
            printed_lines[0], data[0]["date"] + " --> " + data[0]["data"]
        )

        # Check printed action
        self.assertEqual(
            printed_lines[1],
            "{'Response': 'Activating AC for " + str(NB_TICKS) + " ticks'}",
        )

    @patch("requests.get")
    def test_turn_on_heater(self, mock_get):
        # Variables
        action = "TurnOnHeater"
        data = [
            {"date": str(datetime.datetime.now()), "data": str(TEMP_MIN - 1.0)}
        ]

        # Mocked responses
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response.json = lambda: {
            "Response": "Activating Heater for " + str(NB_TICKS) + " ticks"
        }

        # Setup our resquest get mocked (the next request.get will receive our mocked response)
        mock_get.return_value = mock_response

        # Redirect stdout to a temporary buffer (To catch printed lines)
        stdout_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = stdout_buffer

        # Run the code we want to test
        # main = Main()
        self.main.on_sensor_data_received(data)

        # Check that the get request's methode use the correct http URL
        mock_get.assert_called_once_with(
            f"{HOST}/api/hvac/{TOKEN}/{action}/{NB_TICKS}"
        )

        # Get all printed lines during execution
        sys.stdout = old_stdout
        printed_lines = stdout_buffer.getvalue().splitlines()

        # Check printed data
        self.assertEqual(
            printed_lines[0], data[0]["date"] + " --> " + data[0]["data"]
        )

        # Check printed action
        self.assertEqual(
            printed_lines[1],
            "{'Response': 'Activating Heater for "
            + str(NB_TICKS)
            + " ticks'}",
        )

    @patch("requests.get")
    def test_no_action(self, mock_get):
        # Variables
        data = [
            {
                "date": str(datetime.datetime.now()),
                "data": str((TEMP_MIN + TEMP_MAX) / 2),
            }
        ]

        # Mocked responses
        mock_response = requests.Response()

        # Setup our resquest get mocked (the next request.get will receive our mocked response)
        mock_get.return_value = mock_response

        # Redirect stdout to a temporary buffer (To catch printed lines)
        stdout_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = stdout_buffer

        # Run the code we want to test
        # main = Main()
        self.main.on_sensor_data_received(data)

        # Check that no get requests is execute
        self.assertFalse(mock_get.called)

        # Get all printed lines during execution
        sys.stdout = old_stdout
        printed_lines = stdout_buffer.getvalue().splitlines()

        # Check only one line printed
        self.assertEqual(len(printed_lines), 1)

        # Check printed data
        self.assertEqual(
            printed_lines[0], data[0]["date"] + " --> " + data[0]["data"]
        )

    # add a function to test the writing to the database here
    def test_write_to_database(self):

        # Variables
        data = [
            {
                "date": str(datetime.datetime.now()),
                "data": str((TEMP_MIN + TEMP_MAX) / 2),
            }
        ]

        print(data[0]["date"])
        print(data[0]["data"])

        # Run the code we want to test
        #main = Main()
        self.main.push_to_db(date = data[0]["date"], data = data[0]["data"])


        temp_from_bd = get_temperature_by_date(data[0]["date"], SessionLocal())

        print(temp_from_bd)

        # Check that the temperature is not None
        self.assertIsNotNone(temp_from_bd)

        # Check that the temperature is the same as the one we pushed
        self.assertEqual(temp_from_bd.data, data[0]["data"])

        # Check that the date is the same as the one we pushed
        self.assertEqual(temp_from_bd.date, data[0]["date"])

        # Check that the id is not None
        self.assertIsNotNone(temp_from_bd.id)




if __name__ == "__main__":
    unittest.main()
