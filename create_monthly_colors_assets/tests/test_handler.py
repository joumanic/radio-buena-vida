import os
import sys
import unittest
from handler import logic_handler
from unittest.mock import patch, MagicMock

class TestLogicHandler(unittest.TestCase):
    def logic_handler(self):
        response = logic_handler()
        self.assertEqual(response['statusCode'],200)
        self.assertEqual('RBV asset images processed and uploaded succesfully', response['body'])

