from webscrape_utils import setup_driver, get_aws_session, upload_to_s3, write_to_local_file
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape_mcdonalds_turkey():
    country = 'tr'

    driver = setup_driver()
    wait = WebDriverWait(driver, 15)

    driver.get('https://siparis.mcdonalds.com.tr/en')

    driver.find_element(By.XPATH, "//span[text()='Burgerler']").click()

    price_element = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//h5[contains(., 'Big Mac')]/../p[contains(., 'TL')]")))

    big_mac_price = float(price_element.text.split('.')[0])

    session = get_aws_session("credentials/aws.credentials")
    json_string = upload_to_s3(session, country, "BigMac", big_mac_price)
    write_to_local_file("bigmac-price-tr.txt", json_string)

    try:
        driver.quit()
    except Exception:
        pass


if __name__ == "__main__":
    scrape_mcdonalds_turkey()
