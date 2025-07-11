import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.config import DEFAULT_USERNAME, SCREENSHOT_PATH, DASHBOARD_URL

def perform_login(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)

    print("[login] injecting user into localStorage...")
    # preload user session data into localStorage before navigation
    driver.get("http://localhost:28318")
    user_json = f'''
        {{
            "email": "{DEFAULT_USERNAME}",
            "name": "{DEFAULT_USERNAME.split('@')[0].replace('.', ' ').title()}"
        }}
    '''
    driver.execute_script(f'window.localStorage.setItem("user", `{user_json}`);')

    print("[login] navigating directly to dashboard...")
    driver.get(DASHBOARD_URL)

    print("[login] waiting for dashboard content...")
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.text-2xl.font-semibold")))
    except Exception:
        print("[!] dashboard content not detected, login may have failed.")

    print(f"[login] screenshotting dashboard to: {SCREENSHOT_PATH}")
    driver.save_screenshot(SCREENSHOT_PATH)

    print("→ Current URL:", driver.current_url)
    print("→ Page Title:", driver.title)
    print("→ User in localStorage:", driver.execute_script("return window.localStorage.getItem('user');"))