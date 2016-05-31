import logging
import jsonpickle
import threading
from wshubsapi import utils
from concurrent.futures import Future

utils.set_serializer_date_handler()
_message_id = 0
_message_lock = threading.RLock()


class GenericClient(object):
    def __setattr__(self, key, value):
        return super(GenericClient, self).__setattr__(key, value)


class GenericServer(object):
    def __init__(self, hub):
        self.hub = hub

    @classmethod
    def _get_next_message_id(cls):
        global _message_id
        with _message_lock:
            _message_id += 1
            return _message_id

    def _serialize_object(self, obj2ser):
        return jsonpickle.encode(obj2ser, **self.hub.serialization_args)


class GenericBridge(GenericServer):
    def __getattr__(self, function_name):
        def function_wrapper(*args_array):
            """
            :rtype : Future
            """
            args = list()
            args.append(self.clients_ids)
            args.append(function_name)
            args.append(args_array)
            id_ = self._get_next_message_id()
            body = {"hub": self.hub.name, "function": "_client_to_clients_bridge", "args": args, "ID": id_}
            future = self.hub.ws_client.get_future(id_)
            send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
            if isinstance(send_return_obj, Future):
                return send_return_obj
            return future

        return function_wrapper


def construct_api_client_class(client_class):
    if client_class is None:
        from ws4py.client.threadedclient import WebSocketClient
        client_class = WebSocketClient

    class WSHubsAPIClient(client_class):
        def __init__(self, api, url):
            """
            :type api: HubsAPI
            """
            client_class.__init__(self, url)
            self.__futures = dict()
            self.is_opened = False
            self.api = api
            self.log = logging.getLogger(__name__)
            self.log.addHandler(logging.NullHandler())

        def opened(self):
            self.is_opened = True
            self.log.debug("Connection opened")

        def closed(self, code, reason=None):
            self.log.debug("Connection closed with code:\n%s\nAnd reason:\n%s" % (code, reason))

        def received_message(self, m):
            try:
                msg_obj = jsonpickle.decode(m.data.decode('utf-8'))
            except Exception as e:
                self.on_error(e)
                return
            if "reply" in msg_obj:
                f = self.__futures.get(msg_obj["ID"], None)
                if f is None:
                    return
                if msg_obj["success"]:
                    f.set_result(msg_obj["reply"])
                else:
                    f.set_exception(Exception(msg_obj["reply"]))
            else:
                try:
                    client_function = getattr(getattr(self.api, (msg_obj["hub"])).client, msg_obj["function"])
                    replay_message = dict(ID=msg_obj["ID"])
                    try:
                        reply = client_function(*msg_obj["args"])
                        replay_message["reply"] = reply
                        replay_message["success"] = True
                    except Exception as e:
                        replay_message["reply"] = str(e)
                        replay_message["success"] = False
                    finally:
                        self.api.ws_client.send(self.api.serialize_object(replay_message))
                except:
                    self.log.exception("unable to call client function")

            self.log.debug("Message received: %s" % m.data.decode('utf-8'))

        def get_future(self, id_):
            """
            :rtype : Future
            """
            self.__futures[id_] = Future()
            return self.__futures[id_]

        def on_error(self, exception):
            self.log.exception("Error in protocol")

        def default_on_error(self, error):
            pass

    return WSHubsAPIClient


class HubsAPI(object):
    def __init__(self, url, client_class=None, serialization_max_depth=5, serialization_max_iter=100):
        api_client_class = construct_api_client_class(client_class)
        self.ws_client = api_client_class(self, url)
        self.ws_client.default_on_error = lambda error: None
        self.serialization_args = dict(max_depth=serialization_max_depth, max_iter=serialization_max_iter)
        self.serialization_args['unpicklable'] = True
        self.CodeHub = self.CodeHubClass(self.ws_client, self.serialization_args)
        self.VersionsHandlerHub = self.VersionsHandlerHubClass(self.ws_client, self.serialization_args)
        self.LoggingHub = self.LoggingHubClass(self.ws_client, self.serialization_args)
        self.WindowHub = self.WindowHubClass(self.ws_client, self.serialization_args)
        self.UtilsAPIHub = self.UtilsAPIHubClass(self.ws_client, self.serialization_args)
        self.SerialMonitorHub = self.SerialMonitorHubClass(self.ws_client, self.serialization_args)
        self.ConfigHub = self.ConfigHubClass(self.ws_client, self.serialization_args)

    @property
    def default_on_error(self):
        return None

    @default_on_error.setter
    def default_on_error(self, func):
        self.ws_client.default_on_error = func

    def connect(self):
        self.ws_client.connect()

    def serialize_object(self, obj2ser):
        return jsonpickle.encode(obj2ser, self.serialization_args)

    class CodeHubClass(object):
        def __init__(self, ws_client, serialization_args):
            self.name = "CodeHub"
            self.ws_client = ws_client
            self.serialization_args = serialization_args
            self.server = self.ServerClass(self)
            self.client = self.ClientClass()

        def get_clients(self, client_ids):
            return HubsAPI.ChatHubClass.ClientsInServer(client_ids, self)

        class ServerClass(GenericServer):
            
            def get_hex_data(self, code):
                """
                :rtype : Future
                """
                args = list()
                args.append(code)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_hex_data", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def upload_hex(self, hex_text, board, port=None):
                """
                :rtype : Future
                """
                args = list()
                args.append(hex_text)
                args.append(board)
                args.append(port)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "upload_hex", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def upload(self, code, board, port=None):
                """
                :rtype : Future
                """
                args = list()
                args.append(code)
                args.append(board)
                args.append(port)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "upload", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def compile(self, code):
                """
                :rtype : Future
                """
                args = list()
                args.append(code)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "compile", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def upload_hex_file(self, hex_file_path, board, port=None):
                """
                :rtype : Future
                """
                args = list()
                args.append(hex_file_path)
                args.append(board)
                args.append(port)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "upload_hex_file", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

        class ClientClass(GenericClient):
            def __init__(self):
                pass
            

        class ClientsInServer(GenericBridge):
            def __init__(self, client_ids, hub):
                super(self.__class__, self).__init__(hub)
                self.clients_ids = client_ids
            

    class VersionsHandlerHubClass(object):
        def __init__(self, ws_client, serialization_args):
            self.name = "VersionsHandlerHub"
            self.ws_client = ws_client
            self.serialization_args = serialization_args
            self.server = self.ServerClass(self)
            self.client = self.ClientClass()

        def get_clients(self, client_ids):
            return HubsAPI.ChatHubClass.ClientsInServer(client_ids, self)

        class ServerClass(GenericServer):
            
            def set_lib_version(self, version):
                """
                :rtype : Future
                """
                args = list()
                args.append(version)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "set_lib_version", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_lib_version(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_lib_version", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def set_web2board_version(self, version):
                """
                :rtype : Future
                """
                args = list()
                args.append(version)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "set_web2board_version", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_version(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_version", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

        class ClientClass(GenericClient):
            def __init__(self):
                pass
            

        class ClientsInServer(GenericBridge):
            def __init__(self, client_ids, hub):
                super(self.__class__, self).__init__(hub)
                self.clients_ids = client_ids
            

    class LoggingHubClass(object):
        def __init__(self, ws_client, serialization_args):
            self.name = "LoggingHub"
            self.ws_client = ws_client
            self.serialization_args = serialization_args
            self.server = self.ServerClass(self)
            self.client = self.ClientClass()

        def get_clients(self, client_ids):
            return HubsAPI.ChatHubClass.ClientsInServer(client_ids, self)

        class ServerClass(GenericServer):
            
            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_all_buffered_records(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_all_buffered_records", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

        class ClientClass(GenericClient):
            def __init__(self):
                pass
            

        class ClientsInServer(GenericBridge):
            def __init__(self, client_ids, hub):
                super(self.__class__, self).__init__(hub)
                self.clients_ids = client_ids
            

    class WindowHubClass(object):
        def __init__(self, ws_client, serialization_args):
            self.name = "WindowHub"
            self.ws_client = ws_client
            self.serialization_args = serialization_args
            self.server = self.ServerClass(self)
            self.client = self.ClientClass()

        def get_clients(self, client_ids):
            return HubsAPI.ChatHubClass.ClientsInServer(client_ids, self)

        class ServerClass(GenericServer):
            
            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def forceClose(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "forceClose", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

        class ClientClass(GenericClient):
            def __init__(self):
                pass
            

        class ClientsInServer(GenericBridge):
            def __init__(self, client_ids, hub):
                super(self.__class__, self).__init__(hub)
                self.clients_ids = client_ids
            

    class UtilsAPIHubClass(object):
        def __init__(self, ws_client, serialization_args):
            self.name = "UtilsAPIHub"
            self.ws_client = ws_client
            self.serialization_args = serialization_args
            self.server = self.ServerClass(self)
            self.client = self.ClientClass()

        def get_clients(self, client_ids):
            return HubsAPI.ChatHubClass.ClientsInServer(client_ids, self)

        class ServerClass(GenericServer):
            
            def get_hubs_structure(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_hubs_structure", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def is_client_connected(self, client_id):
                """
                :rtype : Future
                """
                args = list()
                args.append(client_id)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "is_client_connected", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_id(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_id", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def set_id(self, client_id):
                """
                :rtype : Future
                """
                args = list()
                args.append(client_id)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "set_id", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

        class ClientClass(GenericClient):
            def __init__(self):
                pass
            

        class ClientsInServer(GenericBridge):
            def __init__(self, client_ids, hub):
                super(self.__class__, self).__init__(hub)
                self.clients_ids = client_ids
            

    class SerialMonitorHubClass(object):
        def __init__(self, ws_client, serialization_args):
            self.name = "SerialMonitorHub"
            self.ws_client = ws_client
            self.serialization_args = serialization_args
            self.server = self.ServerClass(self)
            self.client = self.ClientClass()

        def get_clients(self, client_ids):
            return HubsAPI.ChatHubClass.ClientsInServer(client_ids, self)

        class ServerClass(GenericServer):
            
            def get_all_connected_ports(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_all_connected_ports", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def unsubscribe_from_port(self, port):
                """
                :rtype : Future
                """
                args = list()
                args.append(port)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "unsubscribe_from_port", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_subscribed_clients_ids_to_port(self, port):
                """
                :rtype : Future
                """
                args = list()
                args.append(port)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_subscribed_clients_ids_to_port", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def find_board_port(self, board):
                """
                :rtype : Future
                """
                args = list()
                args.append(board)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "find_board_port", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def is_port_connected(self, port):
                """
                :rtype : Future
                """
                args = list()
                args.append(port)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "is_port_connected", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_available_ports(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_available_ports", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def write(self, port, data):
                """
                :rtype : Future
                """
                args = list()
                args.append(port)
                args.append(data)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "write", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def start_connection(self, port, baudrate=9600):
                """
                :rtype : Future
                """
                args = list()
                args.append(port)
                args.append(baudrate)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "start_connection", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def close_unused_connections(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "close_unused_connections", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def subscribe_to_port(self, port):
                """
                :rtype : Future
                """
                args = list()
                args.append(port)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "subscribe_to_port", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def change_baudrate(self, port, baudrate):
                """
                :rtype : Future
                """
                args = list()
                args.append(port)
                args.append(baudrate)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "change_baudrate", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def close_all_connections(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "close_all_connections", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def close_connection(self, port):
                """
                :rtype : Future
                """
                args = list()
                args.append(port)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "close_connection", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

        class ClientClass(GenericClient):
            def __init__(self):
                pass
            

        class ClientsInServer(GenericBridge):
            def __init__(self, client_ids, hub):
                super(self.__class__, self).__init__(hub)
                self.clients_ids = client_ids
            

    class ConfigHubClass(object):
        def __init__(self, ws_client, serialization_args):
            self.name = "ConfigHub"
            self.ws_client = ws_client
            self.serialization_args = serialization_args
            self.server = self.ServerClass(self)
            self.client = self.ClientClass()

        def get_clients(self, client_ids):
            return HubsAPI.ChatHubClass.ClientsInServer(client_ids, self)

        class ServerClass(GenericServer):
            
            def change_platformio_ini_file(self, content):
                """
                :rtype : Future
                """
                args = list()
                args.append(content)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "change_platformio_ini_file", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def set_libraries_path(self, lib_dir):
                """
                :rtype : Future
                """
                args = list()
                args.append(lib_dir)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "set_libraries_path", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def test_proxy(self, proxyUrl):
                """
                :rtype : Future
                """
                args = list()
                args.append(proxyUrl)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "test_proxy", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def set_proxy(self, proxyUrl):
                """
                :rtype : Future
                """
                args = list()
                args.append(proxyUrl)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "set_proxy", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def set_web_socket_info(self, IP, port):
                """
                :rtype : Future
                """
                args = list()
                args.append(IP)
                args.append(port)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "set_web_socket_info", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def set_log_level(self, logLevel):
                """
                :rtype : Future
                """
                args = list()
                args.append(logLevel)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "set_log_level", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def restore_platformio_ini_file(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "restore_platformio_ini_file", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_config(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_config", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def get_libraries_path(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "get_libraries_path", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def is_possible_libraries_path(self, path):
                """
                :rtype : Future
                """
                args = list()
                args.append(path)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "is_possible_libraries_path", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def set_values(self, config_dic):
                """
                :rtype : Future
                """
                args = list()
                args.append(config_dic)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "set_values", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub.name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.hub.ws_client.get_future(id_)
                send_return_obj = self.hub.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

        class ClientClass(GenericClient):
            def __init__(self):
                pass
            

        class ClientsInServer(GenericBridge):
            def __init__(self, client_ids, hub):
                super(self.__class__, self).__init__(hub)
                self.clients_ids = client_ids
            
