import sqlite3
import argparse

parser = argparse.ArgumentParser(description='db_util provides functionality to interact with the database')
parser.add_argument("-d", action="store", dest="db", default="data.db",
    help="Specify target db")

args = parser.parse_args()

conn = sqlite3.connect(args.db)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS bouts( 
  boutid      INTEGER PRIMARY KEY   NOT NULL,
  eventid     INTEGER               NOT NULL,
  fencer1id   INTEGER               CHECK(fencer1id < fencer2id),
  fencer2id   INTEGER               CHECK(fencer1id < fencer2id),
  score1      INTEGER                       ,
  score2      INTEGER                       ,
  type        TEXT                  CHECK(type in ('de', 'pool'))
);
""")

c.execute("""
CREATE TABLE IF NOT EXISTS events(
  eventid       INTEGER PRIMARY KEY   NOT NULL,
  tournamentid  INTEGER               NOT NULL,
  weapon        TEXT                  CHECK(weapon in ('Epee', 'Foil', 'Saber'))
);
""")

c.execute("""
CREATE TABLE IF NOT EXISTS tournaments(
  tournamentid  INTEGER PRIMARY KEY   NOT NULL,
  start_date    TEXT                  NOT NULL
);
""")

c.execute("""
CREATE TABLE IF NOT EXISTS ratings(
  fencerid            INTEGER               NOT NULL,
  weapon              TEXT                  CHECK(weapon in ('Epee', 'Foil', 'Saber')),
  boutid              INTEGER               NOT NULL,
  ts_mu               REAL                  NOT NULL,
  ts_sigma            REAL                  NOT NULL,
  prev_ts_mu          REAL                  NOT NULL,
  prev_ts_sigma       REAL                  NOT NULL,
  PRIMARY KEY (fencerid, weapon, boutid)
);
""")

c.execute("""
CREATE TABLE IF NOT EXISTS fencers(
  fencerid      INTEGER               NOT NULL,
  first_name    TEXT                  ,
  last_name     TEXT                  ,
  birthyear     INTEGER               NOT NULL,
  usfa_id       INTEGER               ,
  gender        TEXT                  ,
  PRIMARY KEY (fencerid)
);
""")

c.execute("""
CREATE TABLE IF NOT EXISTS promotions(
  fencerid              INTEGER       NOT NULL,
  weapon                TEXT          CHECK(weapon in ('Epee', 'Foil', 'Saber')),
  eventid               INTEGER       NOT NULL,
  rating_earned_letter  TEXT          CHECK(rating_earned_letter in ('A', 'B', 'C', 'D', 'E')),
  rating_earned_year    INTEGER       NOT NULL,
  rating_before_letter  TEXT          CHECK(rating_earned_letter in ('A', 'B', 'C', 'D', 'E', 'U')),
  rating_before_year    INTEGER       ,
  PRIMARY KEY (fencerid, weapon, eventid)
);
""")

# Ties are rounded up
c.execute("""
CREATE TABLE IF NOT EXISTS tournament_results(
  fencerid              INTEGER       NOT NULL,
  eventid               INTEGER       NOT NULL,
  weapon                TEXT          CHECK(weapon in ('Epee', 'Foil', 'Saber')),
  tournamentid          INTEGER       NOT NULL,
  entries               INTEGER       NOT NULL,
  place                 INTEGER       ,
  start_date            TEXT          NOT NULL,
  PRIMARY KEY (fencerid, weapon, eventid, tournamentid)
);
""")
