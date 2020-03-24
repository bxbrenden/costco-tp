import asyncio
from concurrent.futures import ThreadPoolExecutor
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
    tp_dicts = []
    with open(tp_file, 'r') as tpf:
        tp_urls = tpf.read().strip()
        tp_urls = tp_urls.split('\n')
        for line in tp_urls:
            spl = line.split('  ')
            descrip = spl[0]
            url = spl[1]
            tp_dicts.append({descrip: url})
    return tp_dicts


def check_availability(costco_dict, timeout, id_name):
    costco_url = list(costco_dict.values())[0]
    item_description = list(costco_dict.keys())[0]
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get(costco_url)
    try:
        add_to_cart_button = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, id_name))
        )
    except TimeoutException:
        logging.error(f'checkout button was not visible within the {timeout} second timout')
    else:
        #logging.info('successfully found the checkout button')
        stock_status = add_to_cart_button.get_attribute('value')
        stock_message = f'{item_description}: {stock_status}'
        print(stock_message)


async def check_all_stock_async(tp_urls):
    with ThreadPoolExecutor(max_workers=15) as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, check_availability, *(tp_url, 20, 'add-to-cart-btn')) for tp_url in tp_urls]
        for task in await asyncio.gather(*tasks):
            pass


def main():
    configure_logging()

    tp_urls = get_tp_urls('tp_urls.txt')
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(check_all_stock_async(tp_urls))
    loop.run_until_complete(future)


if __name__ == '__main__':
    main()
