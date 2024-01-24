from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
import os

def scrape_mcdonalds_turkey():

    # Get the user's home directory
    home_directory = os.path.expanduser('~')

    # To address an issue caused by the Snap installation of Firefox
    #tmp_dir = os.path.join(home_directory, 'tmp')
    #os.environ['TMPDIR'] = tmp_dir
    #os.system(f"rm -rf {tmp_dir}/*")

    options = FirefoxOptions()
    # options.binary = "/usr/bin/firefox"
    options.add_argument("--headless")  # Run Firefox in headless mode

    # Set preferences for geolocation
    options.set_preference("geo.enabled", True)
    options.set_preference("geo.prompt.testing", True)
    options.set_preference("geo.prompt.testing.allow", False)  # Set to True to allow geolocation

    # service = FirefoxService(executable_path=os.path.join(home_directory, "airflow/geckodriver"))

    driver = webdriver.Firefox(options=options)

    url = 'https://siparis.mcdonalds.com.tr/productv2/?pid=41' # Big Mac product id: 41

    # Open the URL
    driver.get(url)

    # Find the <p> element by its class name
    big_mac_div = driver.find_element(By.CSS_SELECTOR, "div.productDetailDiv p.m-0")

    # Retrieve and print the text from the <p> element
    big_mac_price = big_mac_div.find_element(By.XPATH, "following-sibling::p")

    with open(os.path.join(home_directory,"bigmac-price-tr.txt"), "a") as f:
        f.write(f"{datetime.now().isoformat()} {big_mac_price.text.replace('.', '').replace(',', '.').strip()}\n")

    # Close the driver
    driver.quit()

if __name__ == "__main__":
   scrape_mcdonalds_turkey()
