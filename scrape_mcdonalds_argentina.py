from webscrape_utils import read_credentials, write_string_to_s3, setup_driver, get_aws_session, upload_to_s3, write_to_local_file
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


def scrape_mcdonalds_argentina():
    country = 'ar'

    driver = setup_driver()

    wait = WebDriverWait(driver, 300)  # Adjust the timeout as needed

    url = 'https://www.mcdonalds.com.ar/restaurantes/ciudad-autonoma-de-buenos-aires/cabildo-y-olazabal-bel/pedidos/pedi-y-retira/hamburguesas'
    driver.get(url)

    sleep(1)

    big_mac_price = price_element = wait.until(EC.presence_of_element_located(
    (By.XPATH, "//p[text()='Big Mac']/following-sibling::div//p[@class='font-bold']")))

    big_mac_price = big_mac_price.text.replace("$", "").replace(",", ".").replace(".", "")    

    big_mac_price = float(big_mac_price) / 100

    session = get_aws_session("credentials/aws.credentials")
    json_string = upload_to_s3(session, country, "BigMac", big_mac_price)
    write_to_local_file("bigmac-price-ar.txt", json_string)

    # Close the driver
    driver.quit()

if __name__ == "__main__":
    scrape_mcdonalds_argentina()
