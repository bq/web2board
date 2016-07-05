from optparse import OptionParser


def parse_args():
    parser = OptionParser(usage="usage: %prog [options] filename", version="%prog 1.0")
    parser.add_option("--board", default=Config.web_socket_ip, type='string', action="store", dest="host",
                      help="hostname (localhost)")
    parser.add_option("--port", default=Config.web_socket_port, type='int', action="store", dest="port",
                      help="port (9876)")
    parser.add_option("--test", default='none', type='string', action="store", dest="testing",
                      help="options: [none, unit, integration, all]")
    parser.add_option("--board", default="uno", type='string', action="store", dest="board",
                      help="board connected for integration tests")
    parser.add_option("--logLevel", default=Config.log_level, type='string', action="store", dest="logLevel",
                      help="show more or less info, options[debug, info, warning, error, critical")
    parser.add_option("--update2version", default=None, type='string', action="store", dest="update2version",
                      help="auto update to version")
    parser.add_option("--proxy", default=Config.proxy, type='string', action="store", dest="proxy",
                      help="define proxy for internet connections")
    parser.add_option("--offline", action="store_true", dest="offline", help="communication through console")
    parser.add_option("--server", action="store_true", dest="server", help="communication through http request")


if __name__ == '__main__':




# test runner

import logging

from libs.CompilerUploader import CompilerUploader
import sys

from libs.PathsManager import PathsManager

logging.basicConfig(format='%(message)s', level=logging.DEBUG)
PathsManager.log_relevant_environmental_paths()

code = """
/***   Included libraries  ***/
#include "Arduino.h"
#include <BitbloqUS.h>
#include <Servo.h>


/***   Global variables and function definition  ***/
int led_0 = 13;
US ultrasonidos_0(5, 2);

/***   Setup  ***/
void setup() {
    pinMode(led_0, OUTPUT);
}

/***   Loop  ***/
void loop() {
// turn the LED on (HIGH is the voltage level)
  digitalWrite(LED_BUILTIN, HIGH);
  // wait for a second
  delay(1);
  // turn the LED off by making the voltage LOW
  digitalWrite(LED_BUILTIN, LOW);
   // wait for a second
  delay(30);
}
"""

print sys.argv
c = CompilerUploader.construct()
c._run(code, path=sys.argv[1])