import webapp2
from google.appengine.ext import db
from google.appengine.api import users
import datetime as dt
import sys

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write('Hello, ' + user.nickname())
        else:
            self.redirect(users.create_login_url(self.request.uri))

class Event(db.Model):
    name = db.StringProperty()
    data = db.StringProperty()
    timestamp = db.IntegerProperty()

class EventCountLastMinPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url('/event'))

        userId = user.user_id()
        start = timestampNow() - 60*1000
        name = self.request.get('name')
        handleQuery(self, userId, name, start, sys.maxsize, 10, "true")

class EventCountLast5MinPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url('/event'))

        userId = user.user_id()
        start = timestampNow() - 5*60*1000
        name = self.request.get('name')
        handleQuery(self, userId, name, start, sys.maxsize, 10, "true")

class EventCountPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url('/event'))

        userId = user.user_id()
        delta = self.request.get('delta_millis')
        try:
            if delta:
                start = timestampNow() - long(delta)
            else:
                start = "0"
        except Exception as ex:
            handleException(self, ex)
            return

        name = self.request.get('name')
        handleQuery(self, userId, name, start, sys.maxsize, 10, "true")


class EventPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url('/event'))

        userId = user.user_id()
        name = self.request.get('name')
        start = self.request.get('start')
        end = self.request.get('end')
        limit = self.request.get('limit')
        countOnly = self.request.get('count_only')
        
        events = None

        if not start:
            start = 0

        if not end:
            end = sys.maxsize

        if not limit:
            limit = "10"

        handleQuery(self, userId, name, start, end, limit, countOnly)


class EventAddPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("""
                  <html>
                  <body>
                  <form action="/event/add" method="post">
                    <div><label>Name (e.g. git.commit or mysql.bytes_sent):</label></div>
                    <div><input type="text" name="name"/></div>
                    <div><label>Data:</label></div>
                    <div><input type="text" name="data"/></div>
                    <div><label>Timestamp (e.g. 1384851641000 or the default is now):</label></div>
                    <div><input type="text" name="timestamp"/></div>
                    <input type="submit" value="Add Event" />
                  </form>
                  </body>
                  </html>""")

    def post(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))


        try:
            userId = user.user_id()
            key = defaultKey(userId)
            event = Event(parent=key)
            event.name = self.request.get('name')
            event.data = self.request.get('data')
            timestamp = self.request.get('timestamp')
            event.timestamp = stringToTimestamp(timestamp);
            event.put()
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write('{"status": "OK", "added_event": {"name":"%s", "data":"%s", "timestamp":%d}}' %(event.name, event.data, event.timestamp) )
        except Exception as ex:
            handleException(self, ex)


class EventDeletePage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("""
            <html>
            <body>
            <form action="/event/delete" method="post">
                <div><label>Name(e.g. git.commit, mysql.bytes_sent):</label></div>
                <div><input type="text" name="name"/></div>
                <div><label>start(e.g. 1384851641000 or the default is 0):</label></div>
                <div><input type="text" name="start"/></div>
                <div><label>end(e.g. 1384851641000 or the default is the future):</label></div>
                <div><input type="text" name="end"/></div>
                <input type="submit" value="delete" />
            </form>
            </body>
            </html>
                                """)

    def post(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url('/event'))

        userId = user.user_id()
        name = self.request.get('name')
        start = self.request.get('start')
        end = self.request.get('end')
        if not start:
            start = 0

        if not end:
            end = sys.maxsize

        deleteCount = 0
        try:
            while True:
                events = queryEvents(userId, name, start, end, 1000)
                total = events.count()
                for event in events:
                    event.delete()
                    deleteCount += 1
                if total <= 1000:
                    break
        except Exception as x:
            handleException(self, x)
            return
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write('{"status":"OK", "delete_count": %d}' %deleteCount)


def defaultKey(userId = None):
    return db.Key.from_path('Event', userId or 'default_user_id')

def timestampNow():
    return long(round(float(dt.datetime.now().strftime('%s.%f')),3)*1000)

def stringToTimestamp(date):
    if not date:
        return timestampNow()
    else:
        return long(date)

def queryEvents(userId, name, start, end, limit):
    if name:
        events = db.GqlQuery("SELECT * "
                             "FROM Event "
                             "WHERE ANCESTOR IS :1 AND timestamp >= :2 AND timestamp < :3 AND name = :4 ORDER BY timestamp DESC LIMIT " + str(limit),
                             defaultKey(userId), long(start), long(end), name)
    else:
        events = db.GqlQuery("SELECT * "
                             "FROM Event "
                             "WHERE ANCESTOR IS :1 AND timestamp >= :2 AND timestamp < :3 ORDER BY timestamp DESC LIMIT " + str(limit),
                             defaultKey(userId), long(start), long(end))
    return events



def handleQuery(self, userId, name, start, end, limit, countOnly):
        try:
            events = queryEvents(userId, name, start, end, limit)
        except Exception as x:
            handleExeption(self, x)
            return

        self.response.headers['Content-Type'] = 'application/json'
        total = events.count()
        numOfEvents = total;
        if limit:
            numOfEvents = min(long(limit), total)
        if countOnly:
            self.response.write('{"status": "OK", "total": %d}' % total)
        else:
            self.response.write('{"status": "OK", "total": %d, "num_events": %d,"events":[' % (total, numOfEvents))
            count = 0;
            for event in events:
                if count > 0:
                    self.response.write(',')
                self.response.write('{"name":"%s", "timestamp": %d, "data": "%s"}' % (event.name, event.timestamp, event.data))
                count += 1
            self.response.write(']}')

def handleException(self, ex):
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write('{"status": "FAILED", "error": "%s"}' % ex)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/event/add', EventAddPage),
                               ('/event/delete', EventDeletePage),
                               ('/event', EventPage),
                               ('/event/count/lastmin', EventCountLastMinPage),
                               ('/event/count/last5min', EventCountLast5MinPage),
                               ('/event/count', EventCountPage)],
                               debug=True)

