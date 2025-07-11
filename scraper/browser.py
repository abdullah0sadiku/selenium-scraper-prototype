# Headless browser setup and teardown utilities using Selenium WebDriver

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

def launch_browser(headless=True):
    """
    Launches a Chrome browser instance with optional headless mode.

    Args:
        headless (bool): If True, runs Chrome in headless mode (no GUI).

    Returns:
        webdriver.Chrome: An instance of Chrome WebDriver.
    """
    # Create Chrome options object to customize browser settings
    options = Options()
    if headless:
        # Enable headless mode for running browser without UI
        options.add_argument("--headless=new")

    # Recommended flags for running Chrome in Docker environments
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage") # Since Docker lacks enough shared memory

    # Construct the path to chromedriver.exe located in the current working directory
    chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")
    
    # Set up the ChromeDriver service with the specified executable path
    service = Service(executable_path=chromedriver_path)

    # Initialize the Chrome WebDriver with the defined options and service
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def close_browser(driver):
    """
    Properly closes and quits the given WebDriver instance.

    Args:
        driver (webdriver.Chrome): The Chrome WebDriver instance to close.
    """
    # shut down the browser and end the WebDriver session
    driver.quit()