import logging
import jsonpickle
import threading
from wshubsapi import utils
from concurrent.futures import Future

utils.set_serializer_date_handler()


class WSSimpleObject(object):
    def __setattr__(self, key, value):
        return super(WSSimpleObject, self).__setattr__(key, value)


class GenericServer(object):
    __message_id = 0
    __message_lock = threading.RLock()

    def __init__(self, ws_client, hub_name, serialization_args):
        """
        :type ws_client: WSHubsAPIClient
        """
        self.ws_client = ws_client
        self.hub_name = hub_name
        self.serialization_args = serialization_args

    @classmethod
    def _get_next_message_id(cls):
        with cls.__message_lock:
            cls.__message_id += 1
            return cls.__message_id

    def _serialize_object(self, obj2ser):
        return jsonpickle.encode(obj2ser, **self.serialization_args)


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
                    client_function = self.api.__getattribute__(msg_obj["hub"]).client.__dict__[msg_obj["function"]]
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
                    pass

            self.log.debug("Received message: %s" % m.data.decode('utf-8'))

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
        self.CodeHub = self.__CodeHub(self.ws_client, self.serialization_args)
        self.VersionsHandlerHub = self.__VersionsHandlerHub(self.ws_client, self.serialization_args)
        self.LoggingHub = self.__LoggingHub(self.ws_client, self.serialization_args)
        self.WindowHub = self.__WindowHub(self.ws_client, self.serialization_args)
        self.UtilsAPIHub = self.__UtilsAPIHub(self.ws_client, self.serialization_args)
        self.SerialMonitorHub = self.__SerialMonitorHub(self.ws_client, self.serialization_args)
        self.ConfigHub = self.__ConfigHub(self.ws_client, self.serialization_args)

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

    class __CodeHub(object):
        def __init__(self, ws_client, serialization_args):
            hub_name = self.__class__.__name__[2:]
            self.server = self.__Server(ws_client, hub_name, serialization_args)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def compile(self, code):
                """
                :rtype : Future
                """
                args = list()
                args.append(code)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "compile", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_hex_data(self, code):
                """
                :rtype : Future
                """
                args = list()
                args.append(code)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_hex_data", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "upload", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def upload_hex(self, hexText, board, port=None):
                """
                :rtype : Future
                """
                args = list()
                args.append(hexText)
                args.append(board)
                args.append(port)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "upload_hex", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "upload_hex_file", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

    class __VersionsHandlerHub(object):
        def __init__(self, ws_client, serialization_args):
            hub_name = self.__class__.__name__[2:]
            self.server = self.__Server(ws_client, hub_name, serialization_args)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def get_lib_version(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_lib_version", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_version(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_version", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def set_lib_version(self, version):
                """
                :rtype : Future
                """
                args = list()
                args.append(version)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "set_lib_version", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "set_web2board_version", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

    class __LoggingHub(object):
        def __init__(self, ws_client, serialization_args):
            hub_name = self.__class__.__name__[2:]
            self.server = self.__Server(ws_client, hub_name, serialization_args)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def get_all_buffered_records(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_all_buffered_records", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

    class __WindowHub(object):
        def __init__(self, ws_client, serialization_args):
            hub_name = self.__class__.__name__[2:]
            self.server = self.__Server(ws_client, hub_name, serialization_args)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def forceClose(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "forceClose", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

    class __UtilsAPIHub(object):
        def __init__(self, ws_client, serialization_args):
            hub_name = self.__class__.__name__[2:]
            self.server = self.__Server(ws_client, hub_name, serialization_args)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def get_hubs_structure(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_hubs_structure", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_id(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_id", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "is_client_connected", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "set_id", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

    class __SerialMonitorHub(object):
        def __init__(self, ws_client, serialization_args):
            hub_name = self.__class__.__name__[2:]
            self.server = self.__Server(ws_client, hub_name, serialization_args)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def change_baudrate(self, port, baudrate):
                """
                :rtype : Future
                """
                args = list()
                args.append(port)
                args.append(baudrate)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "change_baudrate", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def close_all_connections(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "close_all_connections", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "close_connection", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def close_unused_connections(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "close_unused_connections", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "find_board_port", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_all_connected_ports(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_all_connected_ports", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_available_ports(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_available_ports", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "get_subscribed_clients_ids_to_port", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "is_port_connected", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "start_connection", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "subscribe_to_port", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "unsubscribe_from_port", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "write", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future

    class __ConfigHub(object):
        def __init__(self, ws_client, serialization_args):
            hub_name = self.__class__.__name__[2:]
            self.server = self.__Server(ws_client, hub_name, serialization_args)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def change_platformio_ini_file(self, content):
                """
                :rtype : Future
                """
                args = list()
                args.append(content)
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "change_platformio_ini_file", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_config(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_config", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_libraries_path(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_libraries_path", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def get_subscribed_clients_ids(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "get_subscribed_clients_ids", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "is_possible_libraries_path", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def restore_platformio_ini_file(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "restore_platformio_ini_file", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "set_libraries_path", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "set_log_level", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "set_proxy", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "set_values", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "set_web_socket_info", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def subscribe_to_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "subscribe_to_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
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
                body = {"hub": self.hub_name, "function": "test_proxy", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
        
            def unsubscribe_from_hub(self, ):
                """
                :rtype : Future
                """
                args = list()
                
                id_ = self._get_next_message_id()
                body = {"hub": self.hub_name, "function": "unsubscribe_from_hub", "args": args, "ID": id_}
                future = self.ws_client.get_future(id_)
                send_return_obj = self.ws_client.send(self._serialize_object(body))
                if isinstance(send_return_obj, Future):
                    return send_return_obj
                return future
