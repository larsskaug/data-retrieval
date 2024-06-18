from webscrape_utils import read_credentials, write_string_to_s3, setup_driver, get_aws_session, upload_to_s3, write_to_local_file
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

def scrape_carrefour():
    country = 'ar'

    driver = setup_driver()

    url = "https://www.carrefour.com.ar/yerba-mate-de-campo-origen-controlado-la-merced-500-g/p"
    driver.get(url)

    sleep(10)  # Adding explicit time due to failure
    product_description = driver.find_element(By.CSS_SELECTOR, "span[class='vtex-store-components-3-x-productBrand vtex-store-components-3-x-productBrand--quickview ']")
    price_element = driver.find_element(By.CSS_SELECTOR, "[class$='valtech-carrefourar-product-price-0-x-sellingPriceValue']")
    price_text = price_element.text.strip().replace("$", "").replace(",", ".").replace(".", "")

    product_name = "yerba-mate"
    price = float(price_text) / 100

    session = get_aws_session("credentials/aws.credentials")
    json_string = upload_to_s3(session, country, product_name, price)
    write_to_local_file("yerba-mate-price-ar.txt", json_string)

    # Close the driver
    driver.quit()

if __name__ == "__main__":
    scrape_carrefour()