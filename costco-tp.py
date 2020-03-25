import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import sys
import time


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

#    options = Options()
#    options.add_argument('--headless')
#    profile = FirefoxProfile(profile_directory='/Users/hydeb/Library/Application Support/Firefox/Profiles/k8merexz.selenium')
#    driver = webdriver.Firefox(firefox_profile=profile, options=options)

    driver = webdriver.Firefox()
    driver.set_window_size(1680, 1050)
    #driver.maximize_window()
    driver.get(costco_url)
    set_postal_code(driver, timeout)
    time.sleep(40)
    check_cart_button(driver, timeout, item_description, id_name)

def check_cart_button(driver, timeout, item_description, id_name):
    try:
        add_to_cart_button = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, id_name))
        )
    except TimeoutException:
        logging.error(f'checkout button was not visible within the {timeout} second timout')
    else:
        stock_status = add_to_cart_button.get_attribute('value')
        stock_message = f'{item_description}: {stock_status}'
        print(stock_message)


def set_postal_code(driver, timeout):
    try:
        label = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.ID, 'delivery-postal-label'))
        )
    except TimeoutException:
        print('postal code setter was not visible within timeout')
    else:
        actions = ActionChains(driver)
        actions.move_to_element(label)
        actions.perform()
        try:
            popover = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'popover'))
            )
        except TimeoutError:
            print('popover was not clickable within timeout threshold')
        else:
            try:
                popover.click()
            except ElementNotInteractableException:
                print('driver could not be clicked though it was labeled as clickable')
            else:
                popover_inputs = popover.find_elements_by_tag_name('input')
                #for index, inp in enumerate(popover_inputs):
                #    attr = inp.get_attribute('type')
                #    if attr.lower().strip() == 'submit':
                #        print(f'The index of the submit input in popover_inputs is {index}')
                try:
                    popover_inputs[0].send_keys('97124')
                except ElementNotInteractableException:
                    print('failed to type zipcode')
                else:
                    try:
                        popover_inputs[3].click()
                    except ElementNotInteractableException:
                        print('could not click submit button for zipcode')
                    else:
                        try:
                            sure_btn = WebDriverWait(driver, timeout).until(
                                EC.element_to_be_clickable((By.ID, 'costcoModalBtn2'))
                            )
                        except TimeoutException:
                            print('timed out before the "sure" button was clickable')
                        else:
                            time.sleep(2)
                            for _ in range(3):
                                time.sleep(2)
                                try:
                                    sure_btn = WebDriverWait(driver, timeout).until(
                                        EC.element_to_be_clickable((By.ID, 'costcoModalBtn2'))
                                    )
                                except TimeoutException:
                                    pass
                                else:
                                    try:
                                        sure_btn.click()
                                    except ElementNotInteractableException:
                                        pass



def has_quantity_input(driver, timeout, product):
    '''returns True if there is a box for specifying item quantity and False otherwise.
       This is used to validate a few false positives that say 'Add to Cart' even when out of stock.'''
    try:
        your_price = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'your-price'))
        )
    except TimeoutException:
        print(f'could not find price box. {product} likely sold out')
        return False
    else:
        try:
            price_val_parent = your_price.find_elements_by_class_name('pull-right')
        except NoSuchElementException:
            print('could not find parent of price box')
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
