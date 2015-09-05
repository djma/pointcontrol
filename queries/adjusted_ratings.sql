DROP TABLE adjusted_ratings;

CREATE TABLE IF NOT EXISTS adjusted_ratings(
  fencerid            INTEGER               NOT NULL,
  weapon              TEXT                  CHECK(weapon in ('Epee', 'Foil', 'Saber')),
  boutid              INTEGER               NOT NULL,
  ts_mu               REAL                  NOT NULL,
  ts_sigma            REAL                  NOT NULL,
  prev_ts_mu          REAL                  NOT NULL,
  prev_ts_sigma       REAL                  NOT NULL,
  PRIMARY KEY (fencerid, weapon, boutid)
);

INSERT INTO adjusted_ratings

SELECT r.fencerid, r.weapon, r.boutid, r.ts_mu + 0.0031825194805194796 * (julianday(t.start_date) - julianday('2010-01-01')) AS ts_mu, r.ts_sigma,
                        r.prev_ts_mu + 0.0031825194805194796 * (julianday(t.start_date) - julianday('2010-01-01')) AS prev_ts_mu, r.prev_ts_sigma
FROM ratings r, bouts b, events e, tournaments t
WHERE r.boutid = b.boutid
  AND b.eventid = e.eventid
  AND e.tournamentid = t.tournamentid
  AND e.weapon = 'Epee'

UNION ALL

SELECT r.fencerid, r.weapon, r.boutid, r.ts_mu + 0.004048614421632449 * (julianday(t.start_date) - julianday('2010-01-01')) AS ts_mu, r.ts_sigma,
                        r.prev_ts_mu + 0.004048614421632449 * (julianday(t.start_date) - julianday('2010-01-01')) AS prev_ts_mu, r.prev_ts_sigma
FROM ratings r, bouts b, events e, tournaments t
WHERE r.boutid = b.boutid
  AND b.eventid = e.eventid
  AND e.tournamentid = t.tournamentid
  AND e.weapon = 'Foil'

UNION ALL

SELECT r.fencerid, r.weapon, r.boutid, r.ts_mu + 0.004551131868131868 * (julianday(t.start_date) - julianday('2010-01-01')) AS ts_mu, r.ts_sigma,
                       r.prev_ts_mu + 0.004551131868131868 * (julianday(t.start_date) - julianday('2010-01-01')) AS prev_ts_mu, r.prev_ts_sigma
FROM ratings r, bouts b, events e, tournaments t
WHERE r.boutid = b.boutid
  AND b.eventid = e.eventid
  AND e.tournamentid = t.tournamentid
  AND e.weapon = 'Saber'
;
