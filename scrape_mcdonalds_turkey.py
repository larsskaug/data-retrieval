from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import os

def scrape_mcdonalds_turkey():

    # Get the user's home directory
    home_directory = os.path.expanduser('~')

    options = ChromeOptions()
    options.add_argument("--headless")  # Run Chromium in headless mode
    options.add_argument("--window-size=2048,2048")

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    options.binary_location = "/usr/bin/chromium-browser"  # Path to Chromium

    # Set geolocation preferences
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['goog:chromeOptions'] = {
        'prefs': {
            'profile.default_content_setting_values.geolocation': 1  # Allow geolocation
        }
    }

    service = ChromeService(executable_path="/usr/lib/chromium-browser/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)

    # Set geolocation coordinates (latitude, longitude, accuracy)
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": -34.56060895367534,
        "longitude": -58.45812919702398,
        "accuracy": 100
    })

    url = 'https://siparis.mcdonalds.com.tr/productv2/?pid=41' # Big Mac product id: 41

    # Open the URL
    driver.get(url)

    # Find the <p> element by its class name
    big_mac_div = driver.find_element(By.CSS_SELECTOR, "div.productDetailDiv p.m-0")

    # Retrieve and print the text from the <p> element
    big_mac_price = big_mac_div.find_element(By.XPATH, "following-sibling::p")

    big_mac_price_details = f"{datetime.now().isoformat()} {big_mac_price.text.replace('.', '').replace(',', '.').strip()}\n"

    print(big_mac_price_details)

    with open(os.path.join(home_directory,"bigmac-price-tr.txt"), "a") as f:
        f.write(big_mac_price_details)

    # Close the driver
    driver.quit()

if __name__ == "__main__":
   scrape_mcdonalds_turkey()
