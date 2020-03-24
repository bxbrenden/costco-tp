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
from selenium.webdriver.firefox.options import Options
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

    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1680, 1050)
    #driver.maximize_window()
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
        if stock_message.lower().strip() == 'add to cart':
            #set_postal_code(driver, timeout)
            if has_quantity_input(driver, timeout, item_description):
                stock_status = 'In Stock'
            else:
                stock_status = 'Out of Stock'
        print(stock_message)


def set_postal_code(driver, timeout):
    try:
        postal_code_inp = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, 'postal-code-input'))
        )
    except TimeoutException:
        logging.error('unable to see postal code input on product page')
        print('unable to see postal code input on product page')
    else:
        try:
            postal_code_inp.click()
        except ElementNotInteractableException:
            logging.error('unable to click postal code input on product page')
            print('unable to click postal code input on product page')
        else:
            postal_code_inp.send_keys('97124')
            try:
                submit = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.ID, 'postal-code-submit'))
                )
            except TimeoutException:
                logging.error('unable to click postal code submit button')
                print('unable to click postal code submit button')


def has_quantity_input(driver, timeout, product):
    '''returns True if there is a box for specifying item quantity and False otherwise.
       This is used to validate a few false positives that say 'Add to Cart' even when out of stock.'''
    try:
        your_price = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'your-price'))
        )
    except TimeoutException:
        print(f'could not find price box. {product} likely sold out')
        sys.exit(1)
        return False
    else:
        try:
            price_val_parent = your_price.find_elements_by_class_name('pull-right')
        except NoSuchElementException:
            print('could not find parent of price box')
            sys.exit(1)
            return False
        else:
            try:
                price_val = price_val_parent.find_elements_by_class_name('value')
            except NoSuchElementException:
                print('could not find price_val')
                return False
            else:
                price = price_val.text
                with open('PRICE.txt', 'a') as pr:
                    pr.write(product + ": " + price)
                return True



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
