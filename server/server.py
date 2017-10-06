import tornado.ioloop
import tornado.web
import sqlite3
import json
import os
import requests
import sys
from tornado.options import define, options
from datetime import datetime, timedelta

allnames = [];
idToName = {};
DBPATH = "/home/ubuntu/data.db"
STATICPATH = "/home/ubuntu/pointcontrol/server/static"
APIKEY = open("/home/ubuntu/pointcontrol/apikey.txt", "r").read().strip()

def _execute(query, args):
        dbPath = DBPATH
        connection = sqlite3.connect(dbPath)
        cursorobj = connection.cursor()
        try:
                cursorobj.execute(query, args)
                result = cursorobj.fetchall()
                connection.commit()
        except Exception:
                raise
        connection.close()
        return result

def loadNames():
    global allnames
    query = ''' select max(start_date), first_name, last_name, f.fencerid, f.birthyear
            from fencers f, tournament_results r
            where f.fencerid = r.fencerid
            group by f.fencerid
            '''
    dbPath = DBPATH
    connection = sqlite3.connect(dbPath)
    cursorobj = connection.cursor()
    try:
            cursorobj.execute(query)
            allnames = cursorobj.fetchall()
            connection.commit()
    except Exception:
            raise
    connection.close()
    for a in allnames:
        idToName[a[3]] = a[1] + " " + a[2]

def getLatestRating(fencerid, weapon):
  getLatestRatingAsOf(fencerid, weapon, datetime.now().isoformat().split("T")[0])

def getLatestRatingAsOf(fencerid, weapon, asof):
  query = ''' select r.ts_mu, t.start_date
          from adjusted_ratings r, bouts b, events e, 
          tournaments t
          where r.boutid = b.boutid
          and r.weapon = (?)
          and b.eventid = e.eventid
          and e.tournamentid = t.tournamentid
          and r.fencerid = (?)
          and t.start_date <= (?)
          order by t.start_date asc, r.boutid asc
          '''
  args = (weapon, int(fencerid), asof)
  rows = _execute(query, args)
  if not rows:
    return None
  return rows[-1]

def matches(query):
        to_return = sorted(filter(lambda x: query.upper() in (x[1].upper() + " " + x[2].upper()), allnames), key = lambda y : (y[1], y[2]))
        if to_return:
            return to_return
        to_return = filter(lambda x: all(q.upper() in (x[1].upper() + " " + x[2].upper()) for q in query.split(" ")), allnames)
        return to_return

class Main(tornado.web.RequestHandler):
    def get(self):
        self.render("main.html")
"""
class AddStudent(tornado.web.RequestHandler):
    def get(self):
        self.render('sqliteform.html')

    def post(self):
        marks = int(self.get_argument("marks"))
        name = self.get_argument("name")
        query = ''' insert into stud (name, marks) values ('%s', %d) ''' %(name, marks);
        _execute(query)
        self.render('success.html')
"""

class RateEventPage(tornado.web.RequestHandler):
    def get(self):
        self.render("rate_events.html")

class GetNames(tornado.web.RequestHandler):
    def get(self):
        q = self.get_argument("q")
        to_return = matches(q)
        result = []
        for x in to_return:
            item = {"t_date" : x[0], "fullname" : x[1] + " " + x[2], "id": x[3], "birthyear": x[4]}
            result.append(item)
        self.write(json.dumps(result))

    def _processresponse(self,rows,fencerid, weapon):
        data_points = {"fencerid" : fencerid, "ratings" : [], "weapon": weapon}
        for row in rows:
                point = {"date": row[1], "rating": row[0]}
                data_points["ratings"].append(point) 
        self.write(json.dumps(data_points))

class GetRating(tornado.web.RequestHandler):
    def get(self):
        fencerid = self.get_argument("id")
        weapon = self.get_argument("weapon")
        query = ''' select r.ts_mu, t.start_date
                from adjusted_ratings r, bouts b, events e, 
                tournaments t
                where r.boutid = b.boutid
                and r.weapon = (?)
                and b.eventid = e.eventid
                and e.tournamentid = t.tournamentid
                and r.fencerid = (?)
                order by t.start_date asc, r.boutid desc
                '''
        args = (weapon, int(fencerid),)
        rows = _execute(query, args)
        self._processresponse(rows,int(fencerid), weapon)

    def _processresponse(self,rows,fencerid, weapon):
        data_points = {"fencerid" : fencerid, "ratings" : [], "weapon": weapon}
        for row in rows:
                point = {"date": row[1], "rating": row[0]}
                data_points["ratings"].append(point) 
        self.write(json.dumps(data_points))

class GetRatingFake(tornado.web.RequestHandler):
    def get(self):
        data_points = {"fencerid": 3, "ratings": [{"date": "2014-03-12", "rating":30}]}
        self.write(json.dumps(data_points))

class GetPlayers(tornado.web.RequestHandler):
    def get(self):
        query = ''' select f.*
                from fencers f
                '''
        dbPath = DBPATH
        connection = sqlite3.connect(dbPath)
        cursorobj = connection.cursor()
        try:
                cursorobj.execute(query)
                rows = cursorobj.fetchall()
                connection.commit()
        except Exception:
                raise
        connection.close()

        players = [];
        for row in rows:
            player = {"name": row[1] + " " + row[2], "id": row[0]}
            players.append(player)
        self.write(json.dumps(players))
        
class GetName(tornado.web.RequestHandler):
    def get(self):
        query = ''' select f.*
                from fencers f
                where f.firstname = b.boutid
                '''
        dbPath = DBPATH
        connection = sqlite3.connect(dbPath)
        cursorobj = connection.cursor()
        try:
                cursorobj.execute(query)
                rows = cursorobj.fetchall()
                connection.commit()
        except Exception:
                raise
        connection.close()

        players = [];
        for row in rows:
            player = {"name": row[1] + " " + row[2], "id": row[0]}
            players.append(player)
        self.write(json.dumps(players))

class GetIDToName(tornado.web.RequestHandler):
    def get(self):
        fencerid = int(self.get_argument("id"))
        obj = {"name": idToName[fencerid]}
        self.write(json.dumps(obj))

class GetEvents(tornado.web.RequestHandler):
    def get(self):
        q = self.get_argument("q")
        payload = {
            "_api_key" : APIKEY,
            "name_contains" : q,
            "_sort" : "start_date_asc",
            "_per_page" : 100,
            "start_date_gte" : (datetime.now() - timedelta(days = 7)).isoformat().split("T")[0],
            }
        r = requests.get("https://api.askfred.net/v1/tournament", params=payload)
        eventinfos = []
        if r.status_code == requests.codes.ok:
            rjson = r.json()
            for tournament in rjson["tournaments"]:
                for event in tournament["events"]:
                    eventinfos.append({
                        "event_id" : event["id"],
                        "tournament_id" : tournament["id"],
                        "tname" : tournament["name"],
                        "ename" : event["full_name"],
                        "weapon" : event["weapon"],
                        "start_date" : tournament["start_date"],
                        })
        self.write(json.dumps(eventinfos))

class RateEvent(tornado.web.RequestHandler):
    def get(self):
        tournament_id = self.get_argument("tournament_id")
        event_id = self.get_argument("event_id")
        payload = {"tournament_id" : tournament_id}
        r = requests.get("https://askfred.net/Events/whoIsComing.php", params=payload)
        datapoints = []
        if r.status_code == requests.codes.ok:
            html = r.text.split("\n")
            i = 0
            weapon = ""
            while not all(s in html[i] for s in ["whoIsComing", str(event_id)]):
                if "Epee" in html[i]:
                    weapon = "Epee"
                elif "Foil" in html[i]:
                    weapon = "Foil"
                elif "Saber" in html[i]:
                    weapon = "Saber"
                i = i+1
            names = []
            while not ("</table>" in html[i]):
                if "," in html[i] and "<td nowrap>" in html[i]:
                    firstlast = html[i].replace("<td nowrap>", "").replace("</td>", "")
                    first = firstlast.split(",")[1].strip()
                    last = firstlast.split(",")[0]
                    names += [first + " " + last]
                i = i+1
            if names != []:
                results = filter(lambda x: x[1] + " " + x[2] in names, allnames)
                for r in results:
                    lr = getLatestRating(r[3], weapon)
                    datapoints += [{"name" : r[1] + " " + r[2], 
                                    "birthyear" : r[4], 
                                    "rating" : lr[0] if lr else None
                                  }]
                datapoints = sorted(datapoints, key = lambda x: x["rating"], reverse=True)
        self.write(json.dumps(datapoints))
       
class IconHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "image/vnd.microsoft.icon")
        with open("favicon.ico", 'rb') as f:
            self.write(f.read())
        return self.flush() 
     
application = tornado.web.Application([
    (r"/", Main),
    (r"/rate_events.html", RateEventPage),
    (r"/get",GetRating),
    (r"/name",GetNames),
    (r"/translate",GetIDToName),
    (r"/event",GetEvents),
    (r"/rate_event",RateEvent),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": STATICPATH}),
    (r"/favicon.ico", IconHandler),
],debug=False)
if __name__ == "__main__":
    tornado.options.parse_command_line()
    loadNames();
    application.listen(sys.argv[1])
    tornado.ioloop.IOLoop.instance().start()
