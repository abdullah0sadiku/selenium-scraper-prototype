import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scraper.browser import launch_browser, close_browser
import time

def test_browser_launch():
    """
    Test function to launch browser, navigate to URL, and print page title
    """

    # Launch a new browser instance and get the driver object
    driver = launch_browser()

    # Navigate to the specified URL and retrieve the page title
    driver.get("https://example.com")
    title = driver.title

    # Print the title of the current page
    print("Title:", title)

    # Wait for 1 second to keep the browser open briefly
    time.sleep(1)

    # Close the browser instance
    close_browser(driver)

    assert "Example" in title