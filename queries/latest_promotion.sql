SELECT p.*, MAX(start_date) as start_date
FROM promotions p, events e, tournaments t
WHERE p.eventid = e.eventid
  AND e.tournamentid = t.tournamentid
GROUP BY p.fencerid;
;
