# Data Retrieval Scripts

The following are python programs that fetch data. They use `selenium` in cases where 
website navigation is required, `requests` where sufficient. 

# Output

All scripts write to a local file, but several also write to S3 buckets.

# Requirements

- Python
- an AWS credential file at the uses root (`~/credentials/aws.credentials`)

# Chromium

Chromium browser needs to be installed

`sudo apt install chromium-browser`

and

`sudo apt-get install chromium-chromedriver`

# Crontab

The following shows an example crontab for the scripts in this repo. I run `crontab -e` as follows `EDITOR=nano crontab -e` because I'm more familar with nano.

```
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin
SCRIPT_PATH=/home/lars/data-retrieval
PY=$SCRIPT_PATH/.venv/bin/python

# Fetch the price of a BigMac in Turkey
0 9 * * * $PY $SCRIPT_PATH/scrape_mcdonalds_turkey.py > $SCRIPT_PATH/logs/scrape_mcdonalds_turkey.log 2>&1

# Fetch the price of Yerba Mate in Argentina
0 10 * * * $PY $SCRIPT_PATH/scrape_carrefour_argentina.py > $SCRIPT_PATH/logs/scrape_carrefour_argentina.log 2>&1

# Fetch the price of a BigMac in Argentina
0 11 * * * $PY $SCRIPT_PATH/scrape_mcdonalds_argentina.py > $SCRIPT_PATH/logs/scrape_mcdonalds_argentina.log 2>&1
```