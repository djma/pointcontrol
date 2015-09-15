#!/bin/bash

python collect_data.py -d /home/ubuntu/data.db --scrape-results --days 7;
python collect_data.py -d /home/ubuntu/data.db --scrape-promotions --days 7;
python collect_data.py -d /home/ubuntu/data.db --scrape-fencer-update;
python rate.py -d /home/ubuntu/data.db --weapon Epee --days 7; 
python rate.py -d /home/ubuntu/data.db --weapon Foil --days 7; 
python rate.py -d /home/ubuntu/data.db --weapon Saber --days 7; 
cat queries/adjusted_ratings.sql | sqlite3 /home/ubuntu/data.db;
