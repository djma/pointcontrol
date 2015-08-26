CREATE TEMP TABLE latest_letter AS
SELECT p.fencerid as fencerid, MAX(t.start_date) AS start_date, rating_earned_letter, rating_earned_year
FROM promotions p, events e, tournaments t
WHERE p.eventid = e.eventid
  AND e.tournamentid = t.tournamentid
GROUP BY p.fencerid
;


SELECT l.*
FROM
(
SELECT r.fencerid, r.weapon, MAX(r.boutid) as boutid, r.ts_mu, r.ts_sigma, l.start_date, l.rating_earned_letter, l.rating_earned_year
FROM adjusted_ratings r LEFT JOIN latest_letter l
ON r.fencerid = l.fencerid
GROUP BY r.fencerid, r.weapon
) l, bouts b, events e, tournaments t
WHERE l.boutid = b.boutid
  AND b.eventid = e.eventid
  AND e.tournamentid = t.tournamentid
  AND t.start_date > '2014-06-20'
;
