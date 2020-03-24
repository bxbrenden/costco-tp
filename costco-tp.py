import logging
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import sys


def configure_logging(log_level=logging.INFO):
    logging.basicConfig(filename='tp_log.txt', level=log_level)

def get_tp_urls(tp_file):
    with open(tp_file, 'r') as tpf:
        tp_urls = tpf.read().strip()
        tp_urls = tp_urls.split('\n')
    return tp_urls


def get_costco_driver(url):
    costco_url = url
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get(costco_url)
    return driver


def check_availability(driver, timeout, id_name):
    try:
        add_to_cart_button = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, id_name))
        )
    except TimeoutException:
        logging.error(f'checkout button was not visible within the {timeout} second timout')
    else:
        logging.info('successfully found the checkout button')
        print('successfully found the checkout button')
        stock = add_to_cart_button.get_attribute('value')
        print(stock)

def main():
    configure_logging()

    tp_urls = get_tp_urls('tp_urls.txt')
    driver = get_costco_driver(tp_urls[0])
    check_availability(driver, 20, 'add-to-cart-btn')


if __name__ == '__main__':
    main()
