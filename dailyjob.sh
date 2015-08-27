#!/bin/bash

python collect_data.py --scrape-results --days 7;
python collect_data.py --scrape-promotions --days 7;
python rate.py --weapon Epee --begin-date 2015-06-01; 
python rate.py --weapon Foil --begin-date 2015-06-01; 
python rate.py --weapon Saber --begin-date 2015-06-01; 
cat queries/adjusted_ratings.sql | sqlite3 data.db;
