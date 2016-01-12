import java.util.concurrent.atomic.AtomicBoolean;

import java.util.Timer;
import java.util.TimerTask;

public class FunctionResult {
	private WSHubsAPIClient connection;
	private int messageID;
	public FunctionResult(WSHubsAPIClient connection, int messageID){
		this.connection = connection;
		this.messageID = messageID;
	}
	public static abstract class Handler{
		private static final int DEFAULT_TIMEOUT = 10000;
		public Handler(){
			this(DEFAULT_TIMEOUT);
			/*new android.os.Handler().postDelayed(
			    new Runnable() {
			        public void run() {
			            Log.i("tag", "This'll run 300 milliseconds later");
			        }
			    }, timeout);*/
		}
		public Handler(int timeout){
			Timer timer = new Timer(true);
			timer.schedule(new TimerTask() {
				@Override
				public void run() {
					if(!done.getAndSet(true))
						onError("TimeOut error");//TODO: return an exception better
				}
			}, timeout);
			
		}
		private AtomicBoolean done = new AtomicBoolean(false);
		public void _onSuccess(Object input){
			if(done.getAndSet(true)) return;
			onSuccess(input);
		};
	    public void _onError(Object input){
	    	if(done.getAndSet(true)) return;
	    	onError(input);
	    };
		public abstract void onSuccess(Object input);
	    public abstract void onError(Object input);
	    public boolean isDone(){return done.get();}
	}
	public synchronized void done(Handler task){
		connection.addReturnFunction(task, messageID);
	}
}
