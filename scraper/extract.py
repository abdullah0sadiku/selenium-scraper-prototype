# handles data scraping logic
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.config import (
    HOMEPAGE1_CONTAINER_SELECTOR,
    HOMEPAGE1_ROW_SELECTOR,
    HOMEPAGE1_FIELD_MAP,
    HOMEPAGE2_ITEM_SELECTOR,
    HOMEPAGE2_FIELD_CLASSES
)

def extract_transactions(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)

    # wait for one of the two UI layouts to appear
    try:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, HOMEPAGE1_CONTAINER_SELECTOR))
        )
        return _extract_homepage1(driver)
    except:
        pass

    try:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, HOMEPAGE2_ITEM_SELECTOR))
        )
        return _extract_homepage2(driver)
    except:
        raise Exception("No known transaction layout found.")

def _extract_homepage1(driver):
    transactions = []
    name_elements = driver.find_elements(By.CSS_SELECTOR, HOMEPAGE1_ROW_SELECTOR)

    for name_el in name_elements:
        try:
            base_id = name_el.get_attribute("id").replace("-name", "")
            name = driver.find_element(By.CSS_SELECTOR, HOMEPAGE1_FIELD_MAP['name'](base_id)).text
            amount = driver.find_element(By.CSS_SELECTOR, HOMEPAGE1_FIELD_MAP['amount'](base_id)).text
            date = driver.find_element(By.CSS_SELECTOR, HOMEPAGE1_FIELD_MAP['date'](base_id)).text

            transactions.append({
                "id": base_id,
                "name": name,
                "amount": amount,
                "date": date
            })
        except Exception:
            continue

    return transactions

def _extract_homepage2(driver):
    items = driver.find_elements(By.CSS_SELECTOR, HOMEPAGE2_ITEM_SELECTOR)
    transactions = []

    for li in items:
        try:
            name = li.find_element(By.CLASS_NAME, HOMEPAGE2_FIELD_CLASSES['name']).text
            merchant = li.find_element(By.CLASS_NAME, HOMEPAGE2_FIELD_CLASSES['merchant']).text
            amount = li.find_element(By.CLASS_NAME, HOMEPAGE2_FIELD_CLASSES['amount']).text

            transactions.append({
                "name": name,
                "merchant": merchant,
                "amount": amount
            })
        except Exception:
            continue

    return transactions
