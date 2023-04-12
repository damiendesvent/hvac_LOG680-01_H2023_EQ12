import os
import unittest
import sys
import io
from unittest.mock import patch
import datetime
from dotenv import load_dotenv
import requests
from src.main import Main
from src.utils import get_event_by_date, get_all_events

load_dotenv()

HOST = os.getenv("HVAC_HOST", "no_host")
TOKEN = os.getenv("HVAC_TOKEN", "no_token")
NB_TICKS = int(os.getenv("HVAC_NB_TICK", "4"))
TEMP_MAX = int(os.getenv("TEMP_MAX", "24"))
TEMP_MIN = int(os.getenv("TEMP_MIN", "18"))


class TestMain(unittest.TestCase):
    def setUp(self):
        self.main = Main()

    # def tearDown(self):
    #     self.main.Base.metadata.drop_all(self.main.engine)

    def test_simulator_up(self):
        response = requests.get(f"{HOST}/api/health")
        self.assertEqual("All system operational Commander !", response.text)

    def get_current_date(self):
        # convert current date to "%Y-%m-%dT%H:%M:%S.%f" format
        date = datetime.datetime.now()
        date = date.strftime("%Y-%m-%dT%H:%M:%S.%f")
        return date

    @patch("requests.get")
    def test_turn_on_ac(self, mock_get):

        date = self.get_current_date()

        # Variables
        action = "TurnOnAc"
        data = [
            {"date": str(date), "data": str(TEMP_MAX + 1.0)}
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

        date = self.get_current_date()

        # Variables
        action = "TurnOnHeater"
        data = [
            {"date": str(date), "data": str(TEMP_MIN - 1.0)}
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
        date = self.get_current_date()

        # Variables
        data = [
            {
                "date": str(date),
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
    def test_write_read_to_database(self):
        # self.main.Base.metadata.create_all(self.main.engine)
        date_now = datetime.datetime.now() # 2021-04-09 12:28:46.119241
        date = date_now.strftime("%Y-%m-%dT%H:%M:%S.%f")

        # Variables
        data = [
            {
                "date": str(date), 
                "data": str((TEMP_MIN + TEMP_MAX) / 2),
            }
        ]

        # Run the code we want to test
        #main = Main()
        self.main.on_sensor_data_received(data)

        date = date_now.strftime("%Y-%m-%d %H:%M:%S") # 2021-04-09 12:28:46

        temp_from_bd = get_event_by_date(date, self.main.db)

        # print(temp_from_bd)

        # Check that the temperature is not None
        self.assertIsNotNone(temp_from_bd)

        # Check that the temperature is the same as the one we pushed
        self.assertEqual(temp_from_bd.data, float(data[0]["data"]))

        # Check that nb_ticks is between 0 and 4
        self.assertGreaterEqual(temp_from_bd.nb_ticks, 0)
        self.assertLessEqual(temp_from_bd.nb_ticks, 4)

        # Check that event is "No-Action" or "TurnOnHeater" or "TurnOnAC"
        self.assertIn(temp_from_bd.event, ["No-Action", "TurnOnHeater", "TurnOnAC"])

        # Check that the date is the same as the one we pushed
        self.assertEqual(str(temp_from_bd.date), str(date))

        # Check that the id  is not None
        self.assertIsNotNone(temp_from_bd.id)


if __name__ == "__main__":
    unittest.main()