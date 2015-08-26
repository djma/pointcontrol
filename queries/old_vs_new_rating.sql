SELECT * FROM
(
  SELECT fencerid, weapon, MAX(boutid) as boutid, ts_mu, ts_sigma
  FROM ratings r
  GROUP BY fencerid
) latest_rating
LEFT JOIN
(
  SELECT p.*, MAX(start_date) as start_date
  FROM promotions p, events e, tournaments t
  WHERE p.eventid = e.eventid
    AND e.tournamentid = t.tournamentid
  GROUP BY p.fencerid
) latest_promotion
ON latest_promotion.fencerid = latest_rating.fencerid
;
