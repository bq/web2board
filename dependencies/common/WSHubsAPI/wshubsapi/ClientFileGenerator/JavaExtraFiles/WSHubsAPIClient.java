import java.net.URI;
import java.net.URISyntaxException;
import java.util.concurrent.atomic.AtomicInteger;

public class WSHubsAPIClient extends WebSocket {
    public static final String TAG = "Websocket";
    private AtomicInteger messageId = new AtomicInteger();

    public int getNewMessageId() {
        return messageId.getAndIncrement();
    }

    public void addReturnFunction(FunctionResult.Handler task, int messageId) {
        WSHubsEventHandler eh = (WSHubsEventHandler) getEventHandler();
        eh.returnFunctions.put(messageId, task);
    }

    public boolean isConnected() {
        return connected;
    }

    public WSHubsAPIClient(String uri) throws URISyntaxException {
        super(new URI(uri));
    }
}