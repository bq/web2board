import inspect
import logging
import os
from os import listdir
from os.path import isfile

from wshubsapi.utils import isFunctionForWSClient, getArgs, ASCII_UpperCase, getModulePath

__author__ = 'jgarc'
log = logging.getLogger(__name__)


class JAVAFileGenerator:
    SERVER_FILE_NAME = "WSHubsApi.java"
    CLIENT_PACKAGE_NAME = "ClientHubs"
    EXTRA_FILES_FOLDER = "JavaExtraFiles"
    CLIENT_HUB_PREFIX = "Client_"

    @classmethod
    def __getHubClassStr(cls, class_):
        funcStrings = "\n".join(cls.__getJSFunctionsStr(class_))
        return cls.CLASS_TEMPLATE.format(name=class_.__HubName__, functions=funcStrings, prefix=cls.CLIENT_HUB_PREFIX)

    @classmethod
    def __getJSFunctionsStr(cls, class_):
        funcStrings = []
        functions = inspect.getmembers(class_, predicate=isFunctionForWSClient)
        for name, method in functions:
            args = getArgs(method)
            types = ["TYPE_" + l for l in ASCII_UpperCase[:len(args)]]
            argsTypes = [types[i] + " " + arg for i, arg in enumerate(args)]
            types = "<" + ", ".join(types) + ">" if len(types) > 0 else ""
            toJson = "\n\t\t\t\t".join([cls.ARGS_COOK_TEMPLATE.format(arg=a) for a in args])
            argsTypes = ", ".join(argsTypes)
            funcStrings.append(cls.FUNCTION_TEMPLATE.format(name=name, args=argsTypes, types=types, cook=toJson))
        return funcStrings

    @classmethod
    def createFile(cls, path, package, hubs):
        if not os.path.exists(path): os.makedirs(path)
        attributesHubs = cls.__getAttributesHubs(hubs)
        with open(os.path.join(path, cls.SERVER_FILE_NAME), "w") as f:
            classStrings = "".join(cls.__getClassStrings(hubs))
            f.write(cls.WRAPPER.format(main=classStrings,
                                         package=package,
                                         clientPackage=cls.CLIENT_PACKAGE_NAME,
                                         attributesHubs=attributesHubs))
        cls.__copyExtraFiles(path, package)

    @classmethod
    def createClientTemplate(cls, path, package, hubs):  # todo: dynamically get client function names
        clientFolder = os.path.join(path, cls.CLIENT_PACKAGE_NAME)
        if not os.path.exists(clientFolder): os.makedirs(clientFolder)
        for hub in hubs:
            clientHubFile = os.path.join(clientFolder, cls.CLIENT_HUB_PREFIX + hub.__HubName__) + '.java'
            if not os.path.exists(clientHubFile):
                with open(clientHubFile, "w") as f:
                    classString = cls.CLIENT_CLASS_TEMPLATE.format(package=package,
                                                                   name=hub.__HubName__,
                                                                   prefix=cls.CLIENT_HUB_PREFIX)
                    f.write(classString)

    @classmethod
    def __getClassStrings(cls, hubs):
        classStrings = []
        for h in hubs:
            classStrings.append(cls.__getHubClassStr(h))
        return classStrings

    @classmethod
    def __getAttributesHubs(cls, hubs):
        return "\n".join([cls.ATTRIBUTE_HUB_TEMPLATE.format(name=hub.__HubName__) for hub in hubs])

    @classmethod
    def __copyExtraFiles(cls, dstPath, package):
        filesPath = os.path.join(getModulePath(), cls.EXTRA_FILES_FOLDER)
        files = [f for f in listdir(filesPath) if isfile(os.path.join(filesPath, f)) and f.endswith(".java")]
        for f in files:
            if not isfile(os.path.join(dstPath, f)):
                absDstPath = os.path.join(dstPath, f)
                absOriPath = os.path.join(filesPath, f)
                with open(absOriPath) as oriFile:
                    with open(absDstPath, 'w') as dstFile:
                        oriStr = oriFile.read()
                        dstStr = "package %s;\n" % package + oriStr
                        dstFile.write(dstStr)
                log.info("Created file: %s", absDstPath)

    CLASS_TEMPLATE = """
    public class {name} {{
        public class Server {{
            public static final String HUB_NAME = "{name}";
            {functions}
        }}
        public Server server = new Server();
        public {prefix}{name} client = new {prefix}{name}(WSHubsApi.this);
    }}"""
    FUNCTION_TEMPLATE = """
            public {types} FunctionResult {name} ({args}) throws JSONException{{
                JSONArray argsArray = new JSONArray();
                {cook}
                return __constructMessage(HUB_NAME, "{name}",argsArray);
            }}"""
    ARGS_COOK_TEMPLATE = "__addArg(argsArray,{arg});"

    WRAPPER = """package {package};
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.json.simple.JSONArray;
import org.json.JSONException;
import org.json.simple.JSONObject;
import java.net.URISyntaxException;
import java.lang.reflect.Modifier;
import {package}.{clientPackage}.*;
public class %s {{//TODO: do not use static functions, we might want different connections
    private static Gson gson = new GsonBuilder()
            .excludeFieldsWithModifiers(Modifier.FINAL, Modifier.TRANSIENT, Modifier.STATIC)
            .serializeNulls()
            .setDateFormat("yyyy/MM/dd HH:mm:ss S")
            .create();
    public WSHubsAPIClient wsClient;
{attributesHubs}

    public %s (String uriStr, WSHubsEventHandler wsHubsEventHandler) throws URISyntaxException {{
        wsClient = new WSHubsAPIClient(uriStr);
        wsHubsEventHandler.setWsHubsApi(this);
        wsClient.setEventHandler(wsHubsEventHandler);
    }}

    public boolean isConnected(){{return wsClient.isConnected();}}

    private FunctionResult __constructMessage (String hubName, String functionName, JSONArray argsArray) throws JSONException{{
        int messageId= wsClient.getNewMessageId();
        JSONObject msgObj = new JSONObject();
        msgObj.put("hub",hubName);
        msgObj.put("function",functionName);
        msgObj.put("args", argsArray);
        msgObj.put("ID", messageId);
        wsClient.send(msgObj.toJSONString());
        return new FunctionResult(wsClient,messageId);
    }}

    private static <TYPE_ARG> void __addArg(JSONArray argsArray, TYPE_ARG arg) throws JSONException {{
        try {{
            if(arg.getClass().isPrimitive())
                argsArray.add(arg);
            else
                argsArray.add(gson.toJsonTree(arg));
        }} catch (Exception e) {{ //todo: do something with this exception
            JSONArray aux = new JSONArray();
            aux.add(gson.toJsonTree(arg));
            argsArray.add(aux);
        }}
    }}
    {main}
}}
    """ % (SERVER_FILE_NAME[:-5], SERVER_FILE_NAME[:-5])

    CLIENT_CLASS_TEMPLATE = """package {package}.%s;
import {package}.ClientBase;
import {package}.WSHubsApi;
public class {prefix}{name} extends ClientBase {{
    public {prefix}{name}(WSHubsApi wsHubsApi) {{
        super(wsHubsApi);
    }}
    // Todo: create client side functions
}}"""%CLIENT_PACKAGE_NAME
    ATTRIBUTE_HUB_TEMPLATE = "    public {name} {name} = new {name}();"
