from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from botocore.exceptions import BotoCoreError, ClientError
from datetime import datetime
import json
import time
import boto3
import os

# Get the user's home directory
home_directory = os.path.expanduser('~')

def read_credentials(file_path):
    with open(file_path, 'r') as file:
        return {key.strip(): value.strip() for key, value in 
                (line.strip().split(' ', 1) for line in file)}

def write_string_to_s3(session, bucket_name, object_key, string_data, attempt=1, max_attempts=2):
    s3 = session.resource('s3')
    object = s3.Object(bucket_name, object_key)

    try:
        object.put(Body=string_data)
        print(f"Successfully uploaded data to {bucket_name}/{object_key}")
    except (BotoCoreError, ClientError) as e:
        if attempt < max_attempts:
            print(f"Failed to upload data on attempt {attempt}: {e}. Retrying...")
            time.sleep(2 ** attempt)  # Exponential backoff
            write_string_to_s3(session, bucket_name, object_key, string_data, attempt + 1, max_attempts)
        else:
            print(f"Failed to upload data after {max_attempts} attempts: {e}")
            raise

def setup_driver():
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=2048,2048")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.binary_location = "/usr/bin/chromium-browser"

    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['goog:chromeOptions'] = {
        'prefs': {
            'profile.default_content_setting_values.geolocation': 1
        }
    }

    service = ChromeService(executable_path="/usr/lib/chromium-browser/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": -34.56060895367534,
        "longitude": -58.45812919702398,
        "accuracy": 100
    })

    return driver


def get_aws_session(credentials_file):
    home_directory = os.path.expanduser('~')
    credentials = read_credentials(os.path.join(home_directory, credentials_file))
    session = boto3.Session(
        aws_access_key_id=credentials['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=credentials['AWS_SECRET_ACCESS_KEY'],
        region_name=credentials['AWS_DEFAULT_REGION']
    )
    return session

def upload_to_s3(session, country, product, price):
    json_data = {
        "country": country,
        "ts": datetime.now().isoformat(),
        "product": product,
        "price": price,
    }
    json_string = json.dumps(json_data)
    bucket_name = 'prices-for-inflation-estimation'
    object_key = f'inflation/{product.lower()}/{product.lower()}-price-{country}-{datetime.now().isoformat()}.json'
    write_string_to_s3(session, bucket_name, object_key, json_string)
    print(f"JSON data uploaded to {bucket_name}/{object_key}")
    return json_string

def write_to_local_file(filename, content):
    home_directory = os.path.expanduser('~')
    with open(os.path.join(home_directory, filename), "a") as f:
        f.write(content + "\n")