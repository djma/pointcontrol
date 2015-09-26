import tornado.ioloop
import tornado.web
import sqlite3
import json
import os
import sys
from tornado.options import define, options

allnames = [];
idToName = {};

def _execute(query, args):
        dbPath = '/home/ubuntu/data.db'
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
    dbPath = '/home/ubuntu/data.db'
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
        dbPath = '/home/ubuntu/data.db'
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
        dbPath = '/home/ubuntu/data.db'
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
       
class IconHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "image/vnd.microsoft.icon")
        with open("favicon.ico", 'rb') as f:
            self.write(f.read())
        return self.flush() 
     
application = tornado.web.Application([
    (r"/", Main),
    (r"/get",GetRating),
    (r"/name",GetNames),
    (r"/translate",GetIDToName),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "/home/ubuntu/pointcontrol/server/static"}),
    (r"/favicon.ico", IconHandler),
],debug=False)
if __name__ == "__main__":
    tornado.options.parse_command_line()
    loadNames();
    application.listen(sys.argv[1])
    tornado.ioloop.IOLoop.instance().start()
