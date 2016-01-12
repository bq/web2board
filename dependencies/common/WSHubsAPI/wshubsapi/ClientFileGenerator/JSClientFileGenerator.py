import inspect
import os

import jsonpickle
from jsonpickle.pickler import Pickler

from wshubsapi.utils import getDefaults, getArgs, isFunctionForWSClient, textTypes

__author__ = 'jgarc'

class JSClientFileGenerator:
    FILE_NAME = "WSHubsApi.js"
    @classmethod
    def __getHubClassStr(cls, class_):
        funcStrings = ",\n".join(cls.__getJSFunctionsStr(class_))
        return cls.CLASS_TEMPLATE.format(name=class_.__HubName__, functions=funcStrings)

    @classmethod
    def __getJSFunctionsStr(cls, class_):
        pickler = Pickler(max_depth=4, max_iter=50, make_refs=False)
        funcStrings = []
        functions = inspect.getmembers(class_.__class__, predicate=isFunctionForWSClient)
        for name, method in functions:
            defaults = getDefaults(method)
            for i,default in enumerate(defaults):
                if not isinstance(default, tuple(textTypes)) or not default.startswith("\""):
                    defaults[i] = jsonpickle.encode(pickler.flatten(default))
            args = getArgs(method)
            defaultsArray = []
            for i, d in reversed(list(enumerate(defaults))):
                defaultsArray.insert(0,cls.ARGS_COOK_TEMPLATE.format(iter = i, name = args[i], default=d))
            defaultsStr = "\n\t\t\t".join(defaultsArray)
            funcStrings.append(cls.FUNCTION_TEMPLATE.format(name=name, args=", ".join(args), cook=defaultsStr, hubName=class_.__HubName__))
        return funcStrings

    @classmethod
    def createFile(cls, path, hubs):
        if not os.path.exists(path): os.makedirs(path)
        with open(os.path.join(path, cls.FILE_NAME), "w") as f:
            classStrings = "".join(cls.__getClassStrings(hubs))
            f.write(cls.WRAPPER.format(main=classStrings))

    @classmethod
    def __getClassStrings(cls, hubs):
        classStrings = []
        for h in hubs:
            classStrings.append(cls.__getHubClassStr(h))
        return classStrings

    WRAPPER = """/* jshint ignore:start */
/* ignore jslint start */
function HubsAPI(url, serverTimeout) {{
    'use strict';

    var messageID = 0,
        returnFunctions = {{}},
        respondTimeout = (serverTimeout || 5) * 1000,
        thisApi = this,
        messagesBeforeOpen = [],
        onOpenTriggers = [];
    url = url || '';

    this.clearTriggers = function () {{
        messagesBeforeOpen = [];
        onOpenTriggers = [];
    }}

    this.connect = function (reconnectTimeout) {{
        reconnectTimeout = reconnectTimeout || -1;
        var openPromise = {{
            onSuccess : function() {{}},
            onError : function(error) {{}},
        }};
        function reconnect(error) {{
            if (reconnectTimeout !== -1) {{
                window.setTimeout(function () {{
                    thisApi.connect(reconnectTimeout);
                    thisApi.callbacks.onReconnecting(error);
                }}, reconnectTimeout * 1000);
            }}
        }}

        try {{
            this.wsClient = new WebSocket(url);
        }} catch (error) {{
            reconnect(error);
            return;
        }}

        this.wsClient.onopen = function () {{
            openPromise.onSuccess();
            openPromise.onError = function () {{}};
            thisApi.callbacks.onOpen(thisApi);
            onOpenTriggers.forEach(function (trigger) {{
                trigger();
            }});
            messagesBeforeOpen.forEach(function (message) {{
                thisApi.wsClient.send(message);
            }});
        }};

        this.wsClient.onclose = function (error) {{
            openPromise.onError(error);
            thisApi.callbacks.onClose(error);
            reconnect(error);
        }};

        this.wsClient.addOnOpenTrigger = function (trigger) {{
            if (thisApi.wsClient.readyState === 0) {{
                onOpenTriggers.push(trigger);
            }} else if (thisApi.wsClient.readyState === 1) {{
                trigger();
            }} else {{
                throw new Error("web socket is closed");
            }}
        }};

        this.wsClient.onmessage = function (ev) {{
            try {{
                var f,
                msgObj = JSON.parse(ev.data);
                if (msgObj.hasOwnProperty('replay')) {{
                    f = returnFunctions[msgObj.ID];
                    if (msgObj.success && f !== undefined && f.onSuccess !== undefined) {{
                        f.onSuccess(msgObj.replay);
                    }}
                    if (!msgObj.success) {{
                        if (f !== undefined && f.onError !== undefined) {{
                            f.onError(msgObj.replay);
			}}
                    }}
                }} else {{
                    f = thisApi[msgObj.hub].client[msgObj.function];
                    f.apply(f, msgObj.args);
                }}
            }} catch (err) {{
                this.onMessageError(err);
            }}
        }};

        this.wsClient.onMessageError = function (error) {{
            thisApi.callbacks.onMessageError(error);
        }};

        return {{ done: function (onSuccess, onError) {{
                openPromise.onSuccess = onSuccess;
                openPromise.onError = onError;
            }}
        }};
    }};

    this.callbacks = {{
        onClose: function (error) {{}},
        onOpen: function () {{}},
        onReconnecting: function () {{}},
        onMessageError: function (error){{}}
    }};

    this.defaultErrorHandler = null;

    var constructMessage = function (hubName, functionName, args) {{
        if(thisApi.wsClient === undefined) {{
            throw Error('ws not connected');
        }}
        args = Array.prototype.slice.call(args);
        var id = messageID++,
            body = {{'hub': hubName, 'function': functionName, 'args': args, 'ID': id}};
        if(thisApi.wsClient.readyState === WebSocket.CONNECTING) {{
            messagesBeforeOpen.push(JSON.stringify(body));
        }} else if (thisApi.wsClient.readyState !== WebSocket.OPEN) {{
            window.setTimeout(function () {{
                var f = returnFunctions[id];
                if (f !== undefined && f.onError !== undefined) {{
                    f.onError('webSocket not connected');
		}}
            }}, 0);
            return {{done: getReturnFunction(id, {{hubName: hubName, functionName: functionName, args: args}})}};
        }}
        else {{
            thisApi.wsClient.send(JSON.stringify(body));
        }}
        return {{done: getReturnFunction(id, {{hubName: hubName, functionName: functionName, args: args}})}};
    }};
    var getReturnFunction = function (ID, callInfo) {{
        return function (onSuccess, onError) {{
            if (returnFunctions[ID] === undefined) {{
                returnFunctions[ID] = {{}};
            }}
            var f = returnFunctions[ID];
            f.onSuccess = function () {{
                if(onSuccess !== undefined) {{
                    onSuccess.apply(onSuccess, arguments);
                }}
                delete returnFunctions[ID];
            }};
            f.onError = function () {{
                if(onError !== undefined) {{
                    onError.apply(onError, arguments);
                }} else if (thisApi.defaultErrorHandler !== null){{
                    var argumentsArray = [callInfo].concat(arguments);
                    thisApi.defaultErrorHandler.apply(thisApi.defaultErrorHandler.apply, argumentsArray);
                }}
                delete returnFunctions[ID];
            }};
            //check returnFunctions, memory leak
            setTimeout(function () {{
                if (returnFunctions[ID] && returnFunctions[ID].onError) {{
                    returnFunctions[ID].onError('timeOut Error');
                }}
            }}, respondTimeout);
        }};
    }};

    {main}
}}
/* jshint ignore:end */
/* ignore jslint end */
    """
    CLASS_TEMPLATE = """
    this.{name} = {{}};
    this.{name}.server = {{
        __HUB_NAME : '{name}',
        {functions}
    }};
    this.{name}.client = {{}};"""

    FUNCTION_TEMPLATE = """
        {name} : function ({args}){{
            {cook}
            return constructMessage('{hubName}', '{name}', arguments);
        }}"""

    ARGS_COOK_TEMPLATE = "arguments[{iter}] = {name} === undefined ? {default} : {name};"
