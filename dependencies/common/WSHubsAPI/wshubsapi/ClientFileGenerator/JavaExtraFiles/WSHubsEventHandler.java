package com.application.jorge.whereappu.WebSocket;
import org.json.JSONObject;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.HashMap;

public abstract class WSHubsEventHandler implements WebSocketEventHandler {
    public HashMap<Integer, FunctionResult.Handler> returnFunctions = new HashMap<>();
    public String clientHubPrefix = WSHubsEventHandler.class.getPackage().getName() + "." + "ClientHubs.Client_";
    protected WSHubsApi wsHubsApi;

    public WSHubsApi getWsHubsApi() {
        return wsHubsApi;
    }

    public void setWsHubsApi(WSHubsApi wsHubsApi) {
        this.wsHubsApi = wsHubsApi;
    }


    @Override
    public void onMessage(WebSocketMessage message) {
        try {
            JSONObject msgObj = new JSONObject(message.getText());
            if (msgObj.has("replay")) {//critical point TODO:use mutex or conditions to prevent concurrent problems
                if (returnFunctions.containsKey(msgObj.getInt("ID"))) {
                    FunctionResult.Handler task = returnFunctions.get(msgObj.getInt("ID"));
                    if (!task.isDone()) {
                        if (msgObj.getBoolean("success"))
                            task._onSuccess(msgObj.get("replay"));
                        else
                            task._onError(msgObj.get("replay"));
                    }
                }
            } else {
                String hubString = msgObj.getString("hub");
                Field hubField = wsHubsApi.getClass().getDeclaredField(hubString);
                Object hubObject =  hubField.get(wsHubsApi);
                Field clientField = hubObject.getClass().getDeclaredField("client");
                Object client = clientField.get(hubObject);
                Class<?> c = Class.forName(clientHubPrefix + hubString);
                Method[] methods = c.getDeclaredMethods();
                String functionName = msgObj.getString("function").toUpperCase();
                for (Method m : methods) {
                    if (m.getName().toUpperCase().equals(functionName)) {
                        int parametersLength = m.getParameterTypes().length;
                        Object[] args = new Object[parametersLength];
                        for (int i = 0; i < parametersLength; i++)
                            args[i] = msgObj.getJSONArray("args").get(i);
                        m.invoke(client, args);//todo get this from reflexion
                        return;
                    }
                }
            }
        } catch (Exception e) {
            System.out.println("ERROR - " + e.toString());
            //Log.e(TAG, "Error " + e.getMessage());
        }
    }

    @Override
    public void onPing() {

    }

    @Override
    public void onPong() {

    }

}
