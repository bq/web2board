import os
import sys
import unittest
from Test.testUtils import TestUtils
from Test.WSCommunication.Hubs.testCodeHub import TestCommProtocol

def runAllTests():
    unittest.main(module=sys.modules[__name__])
    os._exit(1)