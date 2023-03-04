import unittest
import sys
import requests
import json
import os
import io
from src.main import Main
import mysql.connector as mysql
from unittest.mock import patch
from dotenv import load_dotenv
import datetime

load_dotenv()

HOST = os.getenv("HVAC_HOST", 'no_host')
TOKEN = os.getenv("HVAC_TOKEN",'no_token')
NB_TICKS = int(os.getenv("HVAC_NB_TICK",'4'))
TEMP_MAX = int(os.getenv("TEMP_MAX",'18'))
TEMP_MIN = int(os.getenv("TEMP_MIN",'30'))



class TestMain(unittest.TestCase):

    def test_simulator_up(self):
        r = requests.get(f"{HOST}/api/health") 
        self.assertEqual("All system operational Commander !", r.text)
    
    @patch('requests.get')
    def test_TurnOnAc(self, mock_get):
        #Variables
        action = "TurnOnAc"
        data = [{"date" : str(datetime.datetime.now()), "data":str(TEMP_MAX+1.0)}]

        #Mocked responses
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response.json = lambda : {'Response':'Activating AC for '+ str(NB_TICKS) +' ticks'}

        #Setup our resquest get mocked (the next request.get will receive our mocked response)
        mock_get.return_value = mock_response

        #Redirect stdout to a temporary buffer (To catch printed lines)
        stdout_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = stdout_buffer
        
        #Run the code we want to test
        main = Main()
        main.on_sensor_data_received(data)

        #Check that the get request's methode use the correct http URL
        mock_get.assert_called_once_with(f"{HOST}/api/hvac/{TOKEN}/{action}/{NB_TICKS}")

        #Get all printed lines during execution
        sys.stdout = old_stdout
        printedLines = stdout_buffer.getvalue().splitlines()
        
        #Check printed data
        self.assertEqual(printedLines[0], data[0]["date"]  + " --> " + data[0]["data"])

        #Check printed action
        self.assertEqual(printedLines[1], "{'Response': 'Activating AC for "+ str(NB_TICKS) +" ticks'}")

        #Fails a test
        self.assertFalse(True)

    @patch('requests.get')
    def test_TurnOnHeater(self, mock_get):
        #Variables
        action = "TurnOnHeater"
        data = [{"date" : str(datetime.datetime.now()), "data":str(TEMP_MIN-1.0)}]

        #Mocked responses
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response.json = lambda : {'Response':'Activating Heater for '+ str(NB_TICKS) +' ticks'}

        #Setup our resquest get mocked (the next request.get will receive our mocked response)
        mock_get.return_value = mock_response

        #Redirect stdout to a temporary buffer (To catch printed lines)
        stdout_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = stdout_buffer
        
        #Run the code we want to test
        main = Main()
        main.on_sensor_data_received(data)

        #Check that the get request's methode use the correct http URL
        mock_get.assert_called_once_with(f"{HOST}/api/hvac/{TOKEN}/{action}/{NB_TICKS}")

        #Get all printed lines during execution
        sys.stdout = old_stdout
        printedLines = stdout_buffer.getvalue().splitlines()
        
        #Check printed data
        self.assertEqual(printedLines[0], data[0]["date"]  + " --> " + data[0]["data"])

        #Check printed action
        self.assertEqual(printedLines[1], "{'Response': 'Activating Heater for "+ str(NB_TICKS) +" ticks'}")

    
    @patch('requests.get')
    def test_noAction(self, mock_get):
        #Variables
        data = [{"date" : str(datetime.datetime.now()), "data":str((TEMP_MIN+TEMP_MAX)/2)}]

        #Mocked responses
        mock_response = requests.Response()

        #Setup our resquest get mocked (the next request.get will receive our mocked response)
        mock_get.return_value = mock_response

        #Redirect stdout to a temporary buffer (To catch printed lines)
        stdout_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = stdout_buffer
        
        #Run the code we want to test
        main = Main()
        main.on_sensor_data_received(data)

        #Check that no get requests is execute
        self.assertFalse(mock_get.called)

        #Get all printed lines during execution
        sys.stdout = old_stdout
        printedLines = stdout_buffer.getvalue().splitlines()
        
        #Check only one line printed
        self.assertEqual(len(printedLines) ,1)

        #Check printed data
        self.assertEqual(printedLines[0], data[0]["date"]  + " --> " + data[0]["data"])



if __name__ == '__main__':
    unittest.main()
