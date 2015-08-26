SELECT r.*, t.start_date
FROM ratings r, bouts b, events e, tournaments t
WHERE r.boutid = b.boutid
  AND b.eventid = e.eventid
  AND e.tournamentid = t.tournamentid
;
