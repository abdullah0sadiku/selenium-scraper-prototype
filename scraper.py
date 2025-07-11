from scraper.browser import launch_browser, close_browser
from scraper.login import perform_login
from scraper.extract import extract_transactions
from scraper.config import DASHBOARD_URL
import pandas as pd
import time

def main():
    driver = launch_browser(headless=False)  # set to True once stable

    try:
        print("[*] Navigating to login page...")
        perform_login(driver, timeout=20)
        print("[*] Dumping page source after login:")
        print(driver.page_source[:500])

        print("[*] Waiting for dashboard...")
        driver.get(DASHBOARD_URL)
        time.sleep(2)  # optional: give time to render JS content

        print("[*] Extracting transactions...")
        transactions = extract_transactions(driver)
        df = pd.DataFrame(transactions)

        print("[*] Preview of extracted transactions:")
        print(df.head())

    except Exception as e:
        print(f"[!] Error: {e}")

    finally:
        close_browser(driver)
        print("[*] Browser closed.")

if __name__ == "__main__":
    main()
