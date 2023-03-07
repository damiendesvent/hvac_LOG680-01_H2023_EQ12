import unittest
import os
import requests

HOST = os.environ["HVAC_HOST"]


class TestStringMethods(unittest.TestCase):
    def test_simulator_up(self):
        request = requests.get(f"{HOST}/api/health", timeout=10)
        self.assertEqual("All system operational Commander !", request.text)


if __name__ == "__main__":
    unittest.main()
