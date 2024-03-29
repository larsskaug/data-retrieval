# Data Retrieval Scripts

The following are python programs that fetch data. They use `selenium` in cases where 
website navigation is required, `requests` where sufficient. 

# Output

All scripts write to a local file, but several also write to S3 buckets.

# Requirements

- Python
- an AWS credential file at the uses root (`~/credentials/aws.credentials`)

# Crontab

The following shows an example crontab for the scripts in this repo. I run `crontab -e` as follows `EDITOR=nano crontab -e` because I'm more familar with nano.


```
PATH=/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin
SCRIPT_PATH=/Users/larsskaug/data-retrieval
PY=/opt/homebrew/bin/python3

# Fetch the price of a BigMac in Turkey
0 9 * * * * time $PY $SCRIPT_PATH/scrape_mcdonalds_turkey.py > $SCRIPT_PATH/logs/scrape_mcdonalds_turkey.log 2>&1

# Fetch the price of Yerba Mate in Argentina
0 10 * * * * time $PY $SCRIPT_PATH/scrape_carrefour_argentina.py > $SCRIPT_PATH/logs/scrape_carrefour_argentina.log 2>&1

# Fetch the price of a BigMac in Argentina
0 11  * * * * time $PY $SCRIPT_PATH/scrape_mcdonalds_argentina.py > $SCRIPT_PATH/logs/scrape_mcdonalds_argentina.log 2>&1
```
