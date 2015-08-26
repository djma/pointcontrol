--SELECT fencerid, weapon, MAX(boutid) as boutid, ts_mu, ts_sigma
--FROM ratings r
--GROUP BY fencerid
--;


-- This query is different from the above, but *might*
-- be the same if boutids are always sorted by date...
CREATE TEMP TABLE bout_eventid_dates AS
SELECT b.boutid, e.eventid, t.start_date
FROM bouts b, events e, tournaments t
WHERE e.tournamentid = t.tournamentid
  AND b.eventid = e.eventid
;

SELECT AVG(t.ts_mu), COUNT(1), SUM(t.ts_mu), SUM(t.ts_mu * t.ts_mu)
FROM 
(
SELECT r.fencerid, r.weapon, MAX(r.boutid) as boutid, r.ts_mu, r.ts_sigma
FROM ratings r, bout_eventid_dates bed
WHERE r.boutid = bed.boutid
AND COALESCE(bed.start_date, r.fencerid) in
(
  SELECT COALESCE(MAX(bed.start_date), r.fencerid)
  FROM ratings r, bout_eventid_dates bed
  WHERE r.boutid = bed.boutid
    AND bed.start_date < '2011-01-01'
  GROUP BY r.fencerid
)
GROUP BY r.fencerid
) t
;

