import sqlite3
import argparse
import trueskill
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description='rate.py uses Trueskill to rank fencers')
parser.add_argument("-d", action="store", dest="db", default="data.db",
    help="Specify target db")
parser.add_argument("--weapon", action="store", dest="weapon", default=None,
    help="Specify weapon")
parser.add_argument("--days", action="store", dest="scrape_lookback", default=None,
    help="Scrape lookback in calendar days")
parser.add_argument("--begin-date", action="store", dest="begin_date", default=None,
    help="Scrape begin date in yyyy-mm-dd")
parser.add_argument("--end-date", action="store", dest="end_date", default=datetime.now().isoformat().split("T")[0],
    help="Scrape end date in yyyy-mm-dd")

args = parser.parse_args()

conn = sqlite3.connect(args.db, timeout=10)
c = conn.cursor()

end_date = datetime.strptime(args.end_date, '%Y-%m-%d')

if args.begin_date != None:
  begin_date = datetime.strptime(args.begin_date, '%Y-%m-%d')
elif args.scrape_lookback != None:
  begin_date = datetime.now() - timedelta(days=int(args.scrape_lookback))

trueskill.setup(draw_probability=0.0018469)

FENCER_STATE = dict()

def updateRank(bout):
  def getLatestRating(fencerid, weapon):
    if (fencerid, weapon) in FENCER_STATE:
      return FENCER_STATE[(fencerid, weapon)]
    query = c.execute("""
      SELECT r.ts_mu, r.ts_sigma FROM ratings r , bouts b, events e, tournaments t
      WHERE r.fencerid = %(fencerid)s
        AND r.boutid = b.boutid
        AND e.weapon = '%(weapon)s'
        AND b.eventid = e.eventid
        AND e.tournamentid = t.tournamentid
        AND t.start_date < '%(begin_date)s'
      ORDER BY t.start_date desc, b.boutid desc
      LIMIT 1;
      """ % {
        "fencerid" : fencerid,
        "weapon" : weapon,
        "boutid" : boutid,
        "begin_date" : begin_date
        }).fetchone()
    if query:
      return query
    else:
      return (trueskill.MU, trueskill.SIGMA)
  def updateLatestRating(fencerid, weapon, boutid, rating, prev_rating):
    query = c.execute("""
      INSERT OR REPLACE INTO ratings
      (fencerid, weapon, boutid, ts_mu, ts_sigma, prev_ts_mu, prev_ts_sigma)
      VALUES
      (%(fencerid)s, '%(weapon)s', %(boutid)s, %(ts_mu)f, %(ts_sigma)f, %(prev_ts_mu)f, %(prev_ts_sigma)f)
      """ % {
        "fencerid" : fencerid,
        "weapon" : weapon,
        "boutid" : boutid,
        "ts_mu" : rating.mu,
        "ts_sigma" : rating.sigma,
        "prev_ts_mu" : prev_rating.mu,
        "prev_ts_sigma" : prev_rating.sigma,
        })
    FENCER_STATE[(fencerid, weapon)] = (rating.mu, rating.sigma)

  boutid, fencer1id, fencer2id, score1, score2, de_or_pool, weapon, start_date = bout
  oldp1 = getLatestRating(fencer1id, weapon)
  oldp1 = trueskill.Rating(oldp1[0], oldp1[1])
  oldp2 = getLatestRating(fencer2id, weapon)
  oldp2 = trueskill.Rating(oldp2[0], oldp2[1])
  print oldp1, oldp2

  if de_or_pool == "pool":
    if score1 > score2:
      p1, p2 = trueskill.rate_1vs1(oldp1, oldp2)
    elif score2 > score1:
      p2, p1 = trueskill.rate_1vs1(oldp2, oldp1)
    else:
      p1, p2 = trueskill.rate_1vs1(oldp1, oldp2, drawn = True)
  elif de_or_pool == "de":
    # For now... DE's count double
    if score1 > score2:
      p1, p2 = trueskill.rate_1vs1(oldp1, oldp2)
      p1, p2 = trueskill.rate_1vs1(oldp1, oldp2)
    elif score2 > score1:
      p2, p1 = trueskill.rate_1vs1(oldp2, oldp1)
      p2, p1 = trueskill.rate_1vs1(oldp2, oldp1)
    else:
      p1, p2 = trueskill.rate_1vs1(oldp1, oldp2, drawn = True)
      p1, p2 = trueskill.rate_1vs1(oldp1, oldp2, drawn = True)

  updateLatestRating(fencer1id, weapon, boutid, p1, oldp1)
  updateLatestRating(fencer2id, weapon, boutid, p2, oldp2)
  print p1, p2



c_bouts = conn.cursor()

rows = c_bouts.execute("""
    SELECT b.boutid,
           b.fencer1id,
           b.fencer2id,
           b.score1,
           b.score2,
           b.type,
           e.weapon,
           t.start_date
    FROM bouts b, events e, tournaments t
    WHERE b.eventid = e.eventid
      AND e.tournamentid = t.tournamentid
      AND e.weapon = '%(weapon)s'
      AND t.start_date >= '%(begin_date)s'
      AND t.start_date <= '%(end_date)s'
    ORDER BY t.start_date asc, b.boutid asc
    """ % {
      "begin_date" : begin_date,
      "end_date" : end_date,
      "weapon" : args.weapon,
    })

for row in rows:
  print row
  updateRank(row)
conn.commit()
