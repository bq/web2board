import json
import logging
import os
import subprocess
import sys
import time
import urllib2
from optparse import OptionParser
from urllib2 import HTTPError, URLError

from tornado import web, ioloop
from wshubsapi.hubs_inspector import HubsInspector

from Scripts.TestRunner import runAllTests, runIntegrationTests, runUnitTests
from libs import utils
from libs.Config import Config
from libs.Decorators.Asynchronous import asynchronous
from libs.PathsManager import PathsManager
from libs.Updaters.BitbloqLibsUpdater import BitbloqLibsUpdater
from libs.Updaters.Web2boardUpdater import Web2BoardUpdater
from libs.Version import Version
from libs.WSCommunication.Clients.hubs_api import HubsAPI
from libs.WSCommunication.ConnectionHandler import WSConnectionHandler

log = logging.getLogger(__name__)
__mainApp = None


class MainApp:
    def __init__(self):
        Version.read_version_values()
        Config.read_config_file()
        self.w2b_server = None

    @staticmethod
    def __handle_testing_options(testing):
        sys.argv[1:] = []
        if testing != "none":
            if testing == "unit":
                runUnitTests()
            elif testing == "integration":
                runIntegrationTests()
            elif testing == "all":
                runAllTests()

            log.warning("\nexiting program in 10s")
            time.sleep(10)
            os._exit(1)

    @staticmethod
    def parse_system_arguments():
        parser = OptionParser(usage="usage: %prog [options] filename", version="%prog 1.0")
        parser.add_option("--host", default=Config.web_socket_ip, type='string', action="store", dest="host",
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

        return parser.parse_args()

    @asynchronous()
    def update_libraries_if_necessary(self):
        try:
            BitbloqLibsUpdater().restoreCurrentVersionIfNecessary()
        except (HTTPError, URLError) as e:
            log.error("unable to download libraries (might be a proxy problem)")
        except:
            log.exception("unable to copy libraries files, there could be a permissions problem.")

    @asynchronous()
    def check_connection_is_available(self):
        time.sleep(1)
        try:
            api = HubsAPI("ws://{0}:{1}".format(Config.web_socket_ip, Config.web_socket_port))
            api.connect()
        except Exception as e:
            pass
        else:
            log.info("connection available")

    @asynchronous()
    def test_connection(self):
        import socket
        time.sleep(2)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((Config.get_client_ws_ip(), Config.web_socket_port))
        if result == 0:
            log.debug("Port is open")
        else:
            log.error("Port: {} could not be opened, check Antivirus configuration".format(Config.web_socket_port))

    def handle_system_arguments(self, options, args):
        log.info("init web2board with options: {}, and args: {}".format(options, args))
        utils.set_log_level(options.logLevel)
        # self.set_up_proxy(options.proxy)

        if not os.environ.get("platformioBoard", False):
            os.environ["platformioBoard"] = options.board

        if options.proxy is not None:
            Config.proxy = options.proxy

        if options.update2version is not None:
            utils.set_log_level(logging.DEBUG)
            log.debug("updating version")
            Web2BoardUpdater().update(PathsManager.get_dst_path_for_update(options.update2version))

        self.__handle_testing_options(options.testing.lower())

        return options

    def initialize_server_and_communication_protocol(self, options):
        # do not call this line in executable
        if not utils.are_we_frozen():
            HubsInspector.construct_js_file(path="libs/WSCommunication/Clients")
            HubsInspector.construct_js_file(path=os.path.join(os.pardir, "demo", "_static"))
            HubsInspector.construct_python_file(path="libs/WSCommunication/Clients")
        self.w2b_server = web.Application([(r'/(.*)', WSConnectionHandler)])
        Config.web_socket_port = options.port
        self.w2b_server.listen(options.port)
        return self.w2b_server

    def start_server(self, options):
        self.w2b_server = self.initialize_server_and_communication_protocol(options)

        try:
            log.info("listening...")
            # self.checkConnectionIsAvailable()
            ioloop.IOLoop.instance().start()
        finally:
            force_quit()

    def start_main(self):
        PathsManager.clean_pio_envs()
        options, args = self.parse_system_arguments()
        self.handle_system_arguments(options, args)
        self.update_libraries_if_necessary()

        Version.log_data()
        log.debug("Enviromental data:")
        try:
            log.debug(json.dumps(os.environ.data, indent=4, encoding=sys.getfilesystemencoding()))
        except:
            log.exception("unable to log environmental data")
        try:
            PathsManager.log_relevant_environmental_paths()
        except:
            log.exception("Unable to log Paths")
        if options.update2version is None:
            self.start_server(options)
            self.test_connection()


def force_quit():
    try:
        os._exit(1)
    finally:
        pass
