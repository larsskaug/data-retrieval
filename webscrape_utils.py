from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from botocore.exceptions import BotoCoreError, ClientError
from datetime import datetime
import json
import time
import boto3
import os
import shutil


def read_credentials(file_path):
    with open(file_path, 'r') as file:
        return {key.strip(): value.strip() for key, value in
                (line.strip().split(' ', 1) for line in file)}


def write_string_to_s3(session, bucket_name, object_key, string_data, max_attempts=2):
    s3 = session.resource('s3')
    obj = s3.Object(bucket_name, object_key)
    for attempt in range(1, max_attempts + 1):
        try:
            obj.put(Body=string_data)
            print(f"Successfully uploaded data to {bucket_name}/{object_key}")
            return
        except (BotoCoreError, ClientError) as e:
            if attempt < max_attempts:
                print(f"Failed to upload data on attempt {attempt}: {e}. Retrying...")
                time.sleep(2 ** attempt)
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
    options.add_experimental_option('prefs', {
        'profile.default_content_setting_values.geolocation': 1
    })

    driver_candidates = [
        shutil.which("chromedriver"),
        shutil.which("chromium.chromedriver"),
        "/snap/bin/chromium.chromedriver",
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
    ]
    driver_path = next((p for p in driver_candidates if p and os.path.isfile(p)), None)
    if driver_path is None:
        raise FileNotFoundError("chromedriver not found; install chromium-driver or chromedriver")
    service = ChromeService(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": -34.56060895367534,
        "longitude": -58.45812919702398,
        "accuracy": 100
    })

    return driver


def get_aws_session(credentials_file):
    credentials = read_credentials(os.path.join(os.path.expanduser('~'), credentials_file))
    return boto3.Session(
        aws_access_key_id=credentials['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=credentials['AWS_SECRET_ACCESS_KEY'],
        region_name=credentials['AWS_DEFAULT_REGION']
    )


def upload_to_s3(session, country, product, price):
    now = datetime.now().isoformat()
    json_data = {
        "country": country,
        "ts": now,
        "product": product,
        "price": price,
    }
    json_string = json.dumps(json_data)
    bucket_name = 'prices-for-inflation-estimation'
    object_key = f'inflation/{product.lower()}/{product.lower()}-price-{country}-{now}.json'
    write_string_to_s3(session, bucket_name, object_key, json_string)
    print(f"JSON data uploaded to {bucket_name}/{object_key}")
    return json_string


def write_to_local_file(filename, content):
    with open(os.path.join(os.path.expanduser('~'), filename), "a") as f:
        f.write(content + "\n")
