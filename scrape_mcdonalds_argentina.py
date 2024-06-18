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

    url = 'https://www.mcdonalds.com.ar/pedidos/seleccionar-restaurante'
    driver.get(url)

    print("Opened a page with the following title:", driver.title)

    # Pick a restaurant
    addr_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Escribe tu ciudad o tu dirección']")))
    addr_input.send_keys("Avenida Cabildo 2254, Buenos Aires")
    addr_input.send_keys(Keys.RETURN)

    # Select chosen restaurant
    restaurant_selection_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".mcd-restaurant-d-actions .button.is-primary")))
    restaurant_selection_button.click()

    sleep(1)

    # click hamburguesas
    hamburguesas = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Hamburguesas')]")))
    hamburguesas.click()

    # Click Big Mac
    bigmac = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Big Mac')]")))
    bigmac.click()

    # Pick out the price of the Big Mac
    big_mac_div = wait.until(EC.visibility_of_element_located((By.XPATH, '//h4[contains(text(), "Big Mac")]')))
    big_mac_price = big_mac_div.find_element(By.XPATH, "following-sibling::h5")
    big_mac_price = big_mac_price.text.replace("$", "").replace(",", ".").replace(".", "")

    big_mac_price = float(big_mac_price) / 100

    session = get_aws_session("credentials/aws.credentials")
    json_string = upload_to_s3(session, country, "BigMac", big_mac_price)
    write_to_local_file("bigmac-price-ar.txt", json_string)

    # Close the driver
    driver.quit()

if __name__ == "__main__":
    scrape_mcdonalds_argentina()
