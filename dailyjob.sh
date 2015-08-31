#!/bin/bash

python collect_data.py --scrape-results --days 7;
python collect_data.py --scrape-promotions --days 7;
python collect_data.py --scrape-fencer-update;
python rate.py --weapon Epee --days 7; 
python rate.py --weapon Foil --days 7; 
python rate.py --weapon Saber --days 7; 
cat queries/adjusted_ratings.sql | sqlite3 data.db;
