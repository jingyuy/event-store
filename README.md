
How to run the code:
  1. git clone https://github.com/jingyuy/event-store.git under ~DIR/
  2. Install Google App Engine: https://developers.google.com/appengine/downloads
  3. Open Google App Engine: File -> Add Existing Application -> Choose
     the path of ~DIR/event-store/ -> Set Port to 9082 -> Click "Add"
  4. In Google App Engine, choose the application of "event-store" and
     click "Run"

Now the server is ready.


To add some data:
  http://localhost:9082/event/add

To show all events:
  http://localhost:9082/event

Accomplished Assignments:

 * The set of events with a given name (or all events if name is unspecified)
  http://localhost:9082/event?name=git.commit
 * The total number of events that have occurred in the last minute
  http://localhost:9082/event/count/lastmin
 * The total number of events that have occurred in the last 5 minutes
  http://localhost:9082/event/count/last5min
 * The total number of events with a given event name that have occurred in the last minute
  http://localhost:9082/event/count/last5min?name=git.commit
 * The total number of events with a given event name that have occurred in the last 5 minutes
  http://localhost:9082/event/count/last5min?name=git.commit

Bonus
 * Query events within a specified time interval
   http://localhost:9082/event?start=1384857203096&end=1384857215161
 * Support arbitrary time rollups (i.e. not just 1 minute / 5 minute as per above)
   http://localhost:9082/event/count?delta_millis=1000000
 * Explicitly delete events with a given name that arrived within a specified time interval
   http://localhost:9082/event/delete

