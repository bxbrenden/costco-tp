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
            item_name = spl[0]
            url = spl[1]
            tp_dicts.append({item_name: url})
    return tp_dicts


def check_availability(costco_dict, timeout, id_name):
    costco_url = list(costco_dict.values())[0]
    item_name = list(costco_dict.keys())[0]
    print(f'Searching for {item_name}. This will take upwards of 1 minute...')

    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1680, 1050)
    driver.get(costco_url)
    set_postal_code(driver, timeout, item_name)
    time.sleep(65)
    check_cart_button(driver, timeout, item_name, id_name)
    driver.close()

def check_cart_button(driver, timeout, item_name, id_name):
    try:
        add_to_cart_button = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, id_name))
        )
    except TimeoutException:
        logging.error(f'checkout button was not visible within the {timeout} second timout')
    else:
        try:
            cart_btn_visible = WebDriverWait(driver, 6).until(
                EC.visibility_of_element_located((By.ID, 'add-to-cart'))
            )
        except TimeoutException:
            stock_status = 'Out of Stock'
            stock_message = f'{item_name}: {stock_status}'
            print(stock_message)
        else:
            stock_status = add_to_cart_button.get_attribute('value')
            stock_message = f'{item_name}: {stock_status}'
            print(stock_message)


def set_postal_code(driver, timeout, item_name):
    try:
        label = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.ID, 'delivery-postal-label'))
        )
    except TimeoutException:
        print(f'{item_name}: postal code setter was not visible within timeout')
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
