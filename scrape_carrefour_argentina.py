#!/usr/bin/env python3

from datetime import datetime, timedelta
from time import sleep

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import time
import boto3
import json

from botocore.exceptions import BotoCoreError, ClientError

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

def scrape_carrefour():

    country = 'ar'

    # Get the user's home directory
    home_directory = os.path.expanduser('~')

    # To address an issue caused by the Snap installation of Firefox
    #tmp_dir = os.path.join(home_directory, 'tmp')
    #os.environ['TMPDIR'] = tmp_dir
    #os.system(f"rm -rf {tmp_dir}/*")

    #print(f"Does this command look right? rm -rf {tmp_dir}/*")

    options = FirefoxOptions()
    # options.binary = "/opt/homebrew/bin/firefox"
    options.add_argument("--headless")  # Run Firefox in headless mode

    options.add_argument("--width=2048")
    options.add_argument("--height=2048")

    # Set preferences for geolocation
    options.set_preference("geo.enabled", True)
    options.set_preference("geo.prompt.testing", True)
    options.set_preference("geo.prompt.testing.allow", False)  # Set to True to allow geolocation

    # service = FirefoxService(executable_path=os.path.join(home_directory, "airflow/geckodriver"))

    driver = webdriver.Firefox(options=options)

    size = driver.get_window_size()
    #print("Window size: width = {}px, height = {}px".format(size["width"], size["height"]))

    wait = WebDriverWait(driver, 300)  # Adjust the timeout as needed

    url = "https://www.carrefour.com.ar/yerba-mate-de-campo-origen-controlado-la-merced-500-g/p"

    driver.get(url)

    sleep(10) # Adding explicit time due to failure
    product_description = driver.find_element(By.CSS_SELECTOR, "span[class='vtex-store-components-3-x-productBrand vtex-store-components-3-x-productBrand--quickview ']")
    price_element = driver.find_element(By.CSS_SELECTOR, "[class$='valtech-carrefourar-product-price-0-x-sellingPriceValue']")
    price_text = price_element.text.strip().replace("$", "").replace(",", ".").replace(".", "")
                
    credentials = read_credentials(os.path.join(home_directory, "credentials/aws.credentials"))

    # Initialize a Boto3 session
    session = boto3.Session(
        aws_access_key_id=credentials['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=credentials['AWS_SECRET_ACCESS_KEY'],
        region_name=credentials['AWS_DEFAULT_REGION']
    )

    # Your JSON data
    json_data = {
        "country": country,
        "ts": datetime.now().isoformat(),
        "product": product_description.text.strip(),
        "price": float(price_text)/100,
    }

    json_string = json.dumps(json_data)

    # Write the JSON string to S3
    bucket_name = 'prices-for-inflation-estimation'
    object_key = f'inflation/yerba-mate/yerba-mate-price-{country}-{datetime.now().isoformat()}.json'

    write_string_to_s3(session, bucket_name, object_key, json_string)

    print(f"JSON data uploaded to {bucket_name}/{object_key}")

    # Print (append) timestamp and price to file
    with open(os.path.join(home_directory,"yerba-mate-price-ar.txt"), "a") as f:
        f.write(json_string + "\n")
    
    
    # Close the driver
    driver.quit()

if __name__ == "__main__":
    scrape_carrefour()
