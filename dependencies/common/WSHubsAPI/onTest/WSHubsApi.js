function HubsAPI(url, serverTimeout) {
    var messageID = 0;
    var returnFunctions = {};
    var respondTimeout = (serverTimeout || 5) * 1000;
    var thisApi = this;
    var messagesBeforeOpen = [];
    var onOpenTriggers = [];
    url = url || "";

    this.connect = function (reconnectTimeout) {
        reconnectTimeout = reconnectTimeout || -1;

        function reconnect() {
            if (reconnectTimeout != -1) {
                window.setTimeout(function () {
                    thisApi.connect(reconnectTimeout);
                    thisApi.callbacks.onReconnecting();
                }, reconnectTimeout * 1000);
            }
        }

        try {
            this.wsClient = new WebSocket(url);
        } catch (err) {
            reconnect();
        }

        this.wsClient.onopen = function () {
            thisApi.callbacks.onOpen(thisApi);
            onOpenTriggers.forEach(function (trigger) {
                trigger();
            });
            messagesBeforeOpen.forEach(function (message) {
                thisApi.wsClient.send(message);
            });
        };

        this.wsClient.onclose = function (error) {
            thisApi.callbacks.onClose(error);
            reconnect();
        };

        this.wsClient.addOnOpenTrigger = function (trigger) {
            if (thisApi.wsClient.readyState == 0)
                onOpenTriggers.push(trigger);
            else if (thisApi.wsClient.readyState == 1)
                trigger();
            else
                throw new Error("web socket is closed");
        };

        this.wsClient.onmessage = function (ev) {
            var f,
                msgObj;
            try {
                msgObj = JSON.parse(ev.data);
                if (msgObj.hasOwnProperty("replay")) {
                    f = returnFunctions[msgObj.ID];
                    if (msgObj.success && f != undefined && f.onSuccess != undefined)
                        f.onSuccess(msgObj.replay);
                    if (!msgObj.success) {
                        if (f != undefined && f.onError != undefined)
                            f.onError(msgObj.replay);
                    }
                } else {
                    f = thisApi[msgObj.hub].client[msgObj.function];
                    f.apply(f, msgObj.args)
                }
            } catch (err) {
                this.onMessageError(err)
            }
        };

        this.wsClient.onMessageError = function (error) {
            thisApi.callbacks.onMessageError(error);
        };
    };

    this.callbacks = {
        onClose: function (error) {},
        onOpen: function () {},
        onReconnecting: function () {},
        onMessageError: function (error){}
    };

    this.defaultErrorHandler = null;

    var constructMessage = function (hubName, functionName, args) {
        if(thisApi.wsClient === undefined) throw Error("ws not connected");
        args = Array.prototype.slice.call(args);
        var id = messageID++;
        var body = {"hub": hubName, "function": functionName, "args": args, "ID": id};
        if(thisApi.wsClient.readyState === WebSocket.CONNECTING)
            messagesBeforeOpen.push(JSON.stringify(body));
         else if (thisApi.wsClient.readyState !== WebSocket.OPEN) {
            window.setTimeout(function () {
                f = returnFunctions[id];
                if (f != undefined && f.onError != undefined)
                    f.onError("webSocket not connected");
            }, 0);
            return {done: getReturnFunction(id, {hubName: hubName, functionName: functionName, args: args})}
        }
        else
            thisApi.wsClient.send(JSON.stringify(body));
        return {done: getReturnFunction(id, {hubName: hubName, functionName: functionName, args: args})}
    };
    var getReturnFunction = function (ID, callInfo) {
        return function (onSuccess, onError) {
            if (returnFunctions[ID] == undefined)
                returnFunctions[ID] = {};
            var f = returnFunctions[ID];
            f.onSuccess = function () {
                if(onSuccess !== undefined)
                    onSuccess.apply(onSuccess, arguments);
                delete returnFunctions[ID]
            };
            f.onError = function () {
                if(onError !== undefined)
                    onError.apply(onError, arguments);
                else if (thisApi.defaultErrorHandler != null){
                    var argumentsArray = [callInfo].concat(arguments);
                    thisApi.defaultErrorHandler.apply(thisApi.defaultErrorHandler.apply, argumentsArray);
                }
                delete returnFunctions[ID]
            };
            //check returnFunctions, memory leak
            setTimeout(function () {
                if (returnFunctions[ID] && returnFunctions[ID].onError)
                    returnFunctions[ID].onError("timeOut Error");
            }, respondTimeout)
        }
    };

    
    this.TestHub = {};
    this.TestHub.server = {
        __HUB_NAME : "TestHub",
        
        getData : function (){
            
            return constructMessage(this.__HUB_NAME, "getData",arguments);
        }
    };
    this.TestHub.client = {};
    this.TestHub2 = {};
    this.TestHub2.server = {
        __HUB_NAME : "TestHub2",
        
        getData : function (){
            
            return constructMessage(this.__HUB_NAME, "getData",arguments);
        }
    };
    this.TestHub2.client = {};
}
    