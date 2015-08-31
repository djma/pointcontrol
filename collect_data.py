import time
import json
import requests
import argparse
import sqlite3
from datetime import datetime, timedelta

# Global vars
API_KEY = ""
db = None
conn = None

def isStringInt(s):
  try: 
    int(s)
    return True
  except ValueError:
    return False

def parseEvent(event_id):
  def parsePool(pool):
    #TODO: merge duplicate code with parseDE
    try:
      bouts = pool["bouts"]
    except:
      return
    for bout in bouts:
      if "fencers" not in bout:
        continue
      fs = bout["fencers"]
      if len(fs) != 2:
        continue
      i,j = 0,1
      if fs[0]["id"] > fs[1]["id"]:
        i,j = 1,0
      db.execute("""
        INSERT OR IGNORE INTO bouts 
        (boutid, eventid, fencer1id, fencer2id, score1, score2, 'type')
        VALUES
        (%(boutid)s, %(eventid)s, %(fencer1id)s, %(fencer2id)s, %(score1)s, %(score2)s, '%(type)s')
        """ % {
          "boutid" : bout["id"],
          "eventid" : event_id,
          "fencer1id" : fs[i]["id"],
          "fencer2id" : fs[j]["id"],
          "score1" : fs[i]["score"],
          "score2" : fs[j]["score"],
          "type" : "pool",
          })

  def parseDE(de_table):
    #TODO: merge duplicate code with parsePool
    try:
      bouts = de_table["bouts"]
    except:
      return
    for bout in bouts:
      if "fencers" not in bout:
        continue
      fs = bout["fencers"]
      i,j = 0,1
      if len(fs) != 2:
        continue
      if fs[0]["id"] > fs[1]["id"]:
        i,j = 1,0
      if len(fs) == 2: # In case of a bye
        db.execute("""
          INSERT OR IGNORE INTO bouts 
          (boutid, eventid, fencer1id, fencer2id, score1, score2, 'type')
          VALUES
          (%(boutid)s, %(eventid)s, %(fencer1id)s, %(fencer2id)s, %(score1)s, %(score2)s, '%(type)s')
          """ % {
            "boutid" : bout["id"],
            "eventid" : event_id,
            "fencer1id" : fs[i]["id"],
            "fencer2id" : fs[j]["id"],
            "score1" : fs[i]["score"],
            "score2" : fs[j]["score"],
            "type" : "de",
            })

  payload = {"_api_key" : API_KEY,
    "_per_page" : "100", # won't be more than 100 events in a tournament right?
    "event_id" : event_id,
    }
  r = requests.get("https://api.askfred.net/v1/roundresult", params=payload)
  if r.status_code == 500:
    print "Request failed with code 500. Payload: " + "https://api.askfred.net/v1/roundresult" + str(payload)
    return

  event_results = r.json()
  if int(event_results["total_matched"]) > 100:
    raise Exception("more than 100 roundresult with same id, wtf. event_id = " + event_id)
  rnds = event_results["rounds"]
  for rnd in rnds:
    if rnd["round_type"] == "pool":
      for pool in rnd["pools"]:
        parsePool(pool)
    elif rnd["round_type"] in ("de", "fo3", "apf8", "rep16"):
      for de_table in rnd["de_tables"]:
        parseDE(de_table)
    else:
      with open("to_verify.txt", "a") as f:
        f.write(rnd["round_type"] + " in eventid=" + str(event_id))
      for de_table in rnd["de_tables"]:
        parseDE(de_table)


def scrapeResults(begin_date, end_date):
  i = 1
  batch_num = 100
  while True:
    payload = {"_api_key" : API_KEY,
      "_sort" : "start_date_desc",
      "_per_page" : batch_num,
      "_page" : i,
      "start_date_lte" : end_date.isoformat().split("T")[0],
      "start_date_gte" : begin_date.isoformat().split("T")[0],
      }
    r = requests.get("https://api.askfred.net/v1/tournament", params=payload)
    rjson = r.json()

    for tournament in rjson["tournaments"]:
      print "parsing " + str(tournament["id"])
      if db.execute("SELECT * FROM tournaments WHERE tournamentid = " + str(tournament["id"])).fetchone():
        continue
      print tournament
      print tournament["start_date"]
      sql_insert = "INSERT OR IGNORE INTO tournaments (tournamentid, start_date) VALUES (%(tid)s, '%(sd)s');" % {"tid" : tournament["id"], "sd" : tournament["start_date"]}
      db.execute(sql_insert)
      if "events" not in tournament:
        continue
      for event in tournament["events"]:
        db.execute("""INSERT OR IGNORE INTO events
          (eventid, tournamentid, weapon)
          VALUES
          (%(eventid)s, %(tournamentid)s, '%(weapon)s')""" % {
            "eventid" : event["id"],
            "tournamentid" : event["tournament_id"],
            "weapon" : event["weapon"],
          })
        try:
          parseEvent(event["id"])
        except:
          time.sleep(10)
          parseEvent(event["id"])
      conn.commit()
      time.sleep(10)


    if i * batch_num >= int(rjson["total_matched"]):
      break
    i = i+1

def scrapePromotions(begin_date, end_date):
  i = 1
  batch_num = 100
  while True:
    payload = {"_api_key" : API_KEY,
      "_sort" : "tournament_start_date_desc",
      "_per_page" : batch_num,
      "_page" : i,
      "tournament_start_date_lte" : end_date.isoformat().split("T")[0],
      "tournament_start_date_gte" : begin_date.isoformat().split("T")[0],
      }
    r = requests.get("https://api.askfred.net/v1/result", params=payload)
    rjson = r.json()

    for result in rjson["results"]:
      db.execute("""INSERT OR IGNORE INTO tournament_results
        (fencerid, eventid, weapon, tournamentid, entries, place, start_date)
        VALUES
        (%(f)s, %(e)s, '%(w)s', %(t)s, %(entries)s, %(place)s, '%(start_date)s')
      """ % {
          "f" : result["competitor_id"],
          "e" : result["event_id"],
          "w" : result["weapon"],
          "t" : result["tournament_id"],
          "entries" : result["entries"],
          "place" : result["place"],
          "start_date" : result["tournament_start_date"],
        })

      if "rating_Earned_letter" in result:
        db.execute("""INSERT OR IGNORE INTO promotions
          (fencerid, weapon, eventid, rating_earned_letter, rating_earned_year, rating_before_letter, rating_before_year)
          VALUES
          (%(f)s, '%(w)s', %(e)s, '%(letter)s', %(year)s, '%(bletter)s', %(byear)s)
        """ % {
          "f" : result["competitor_id"],
          "e" : result["event_id"],
          "w" : result["weapon"],
          "letter" : result["rating_Earned_letter"],
          "year" : result["rating_Earned_year"],
          "bletter" : result["rating_before_letter"],
          "byear" : result["rating_before_year"] if "rating_before_year" in result else "NULL",
          })
        print result["competitor_id"], result["weapon"], result["rating_Earned_letter"], result["tournament_start_date"]
    conn.commit()
    if i * batch_num >= int(rjson["total_matched"]):
      break
    i = i+1
    time.sleep(10)

def scrapeAllFencers(begin_fencerid=0):
  i = 1
  batch_num = 100
  current_fencerid = None
  while True:
    payload = {"_api_key" : API_KEY,
      "_sort" : "fencer_id_desc",
      "_per_page" : batch_num,
      "_page" : i,
      }
    r = requests.get("https://api.askfred.net/v1/fencer", params=payload)
    rjson = r.json()

    for result in rjson["fencers"]:
      sqlcmd = ("""INSERT OR IGNORE INTO fencers
        (fencerid, first_name, last_name, birthyear, usfa_id, gender)
        VALUES
        (%(f)s, '%(fn)s', '%(ln)s', %(b)s, %(uid)s, '%(g)s')
      """ % {
          "f" : result["id"],
          "fn" : result["first_name"].replace("'", "''"), #retarded sql escaping
          "ln" : result["last_name"].replace("'", "''"), #retarded sql escaping
          "b" : result["birthyear"],
          "uid" : result["usfa_id"] if (result["usfa_id"] != "" and isStringInt(result["usfa_id"]) ) else "NULL",
          "g" : result["gender"],
        })
      print sqlcmd
      db.execute(sqlcmd)
      current_fencerid = int(result["id"])

    conn.commit()

    if i * batch_num >= int(rjson["total_matched"]):
      break
    if current_fencerid < begin_fencerid:
      break
    i = i+1
    time.sleep(10)
  return

def scrapeAllFencersUpdate():
  maxfencerid = int(db.execute("SELECT MAX(fencerid) FROM fencers").fetchone())
  scrapeAllFencers(maxfencerid)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Collects Askfred bout data')
  parser.add_argument("-k", action="store", dest="API_KEY", default="96dcd9772df668624c1b320cc5f185b1",
      help="Askfred REST API key")
  parser.add_argument("-d", action="store", dest="db", default="data.db",
      help="db target")
  parser.add_argument("--scrape-results", action="store_true", dest="scrape_results", default=False,
      help="Scrape tournament results. Must use with either --days or --begin-date")
  parser.add_argument("--scrape-promotions", action="store_true", dest="scrape_promotions", default=False,
      help="Scrape promotions. Must use with either --days or --begin-date")
  parser.add_argument("--scrape-fencer", action="store_true", dest="scrape_fencer", default=False,
      help="Scrape fencers.")
  parser.add_argument("--scrape-fencer-update", action="store_true", dest="scrape_fencer_update", default=False,
      help="Scrape fencers (only update).")
  parser.add_argument("--days", action="store", dest="scrape_lookback", default=None,
      help="Scrape lookback in calendar days")
  parser.add_argument("--begin-date", action="store", dest="begin_date", default=None,
      help="Scrape begin date in yyyy-mm-dd")
  parser.add_argument("--end-date", action="store", dest="end_date", default=datetime.now().isoformat().split("T")[0],
      help="Scrape end date in yyyy-mm-dd")
  args = parser.parse_args()

  API_KEY = args.API_KEY
  conn = sqlite3.connect(args.db, timeout=20)
  db = conn.cursor()
  end_date = datetime.strptime(args.end_date, '%Y-%m-%d')

  if args.scrape_fencer or args.scrape_fencer_update:
    begin_date = datetime.now()
    end_date = datetime.now()

  if args.begin_date != None:
    begin_date = datetime.strptime(args.begin_date, '%Y-%m-%d')
  elif args.scrape_lookback != None:
    begin_date = datetime.now() - timedelta(days=int(args.scrape_lookback))

  print begin_date, end_date

  if args.scrape_results:
    scrapeResults(begin_date, end_date)
  elif args.scrape_promotions:
    scrapePromotions(begin_date, end_date)
  elif args.scrape_fencer:
    scrapeAllFencers()
  elif args.scrape_fencer_update:
    scrapeAllFencersUpdate()

  conn.commit()
  conn.close()
    

#parseEvent(118025)
