SELECT r.fencerid, r.weapon, MAX(r.boutid) AS boutid, r.ts_mu, r.ts_sigma,
  p.rating_earned_letter, 
  p.rating_earned_year, 
  p.rating_before_letter, 
  p.rating_before_year,
  t.start_date
FROM adjusted_ratings r, bouts b, promotions p, events e, tournaments t
WHERE p.weapon = r.weapon
  AND e.weapon = r.weapon
  AND r.fencerid = p.fencerid
  AND r.boutid = b.boutid
  AND b.eventid = p.eventid
  AND b.eventid = e.eventid
  AND e.tournamentid = t.tournamentid
GROUP BY r.fencerid, p.eventid, r.weapon
ORDER BY t.start_date ASC, r.boutid ASC;
