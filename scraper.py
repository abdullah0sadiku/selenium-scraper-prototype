#!/usr/bin/env python3
"""
Main scraper entry point with aggressive login spamming.
"""

import sys
import time
import pandas as pd
from scraper.browser import launch_browser, close_browser
from scraper.login import perform_login
from scraper.extract import extract_transactions

def export_to_csv(transactions):
    """
    Export transactions to CSV file.
    """
    if not transactions:
        print("No transactions to export")
        return
        
    df = pd.DataFrame(transactions)
    output_path = "output/transactions.csv"
    df.to_csv(output_path, index=False)
    print(f"Exported {len(transactions)} transactions to {output_path}")

def main():
    """
    Main scraper function with aggressive login approach.
    """
    print("🚀 Starting BankDashboard Scraper with Aggressive Login...")
    print("=" * 60)
    
    driver = None
    try:
        # Create browser instance
        print("📱 Creating browser instance...")
        driver = launch_browser(headless=False)
        
        # Perform aggressive login
        print("🔐 Starting aggressive login process...")
        print("   This will spam login attempts until successful!")
        perform_login(driver)
        
        # Verify we're actually logged in
        current_url = driver.current_url
        page_title = driver.title
        
        print(f"✅ Login process completed!")
        print(f"   Current URL: {current_url}")
        print(f"   Page Title: {page_title}")
        
        # Check if we have real dashboard content
        from scraper.login import is_real_dashboard_content
        if is_real_dashboard_content(driver):
            print("🎉 SUCCESS: Real dashboard content detected!")
        else:
            print("⚠️  WARNING: May still be showing login form")
            print("   Extraction may find limited data")
        
        # Extract transactions
        print("\n💰 Extracting transaction data...")
        transactions = extract_transactions(driver)
        
        if transactions:
            print(f"✅ Found {len(transactions)} transactions")
            
            # Export to CSV
            print("📊 Exporting to CSV...")
            export_to_csv(transactions)
            print("✅ Export completed successfully!")
            
        else:
            print("❌ No transactions found")
            print("   This could mean:")
            print("   - Login wasn't fully successful")
            print("   - Page selectors need updating")
            print("   - Dashboard is still loading")
            
            # Take debug screenshot
            screenshot_path = "output/debug_no_transactions.png"
            driver.save_screenshot(screenshot_path)
            print(f"   Debug screenshot saved: {screenshot_path}")
            
    except KeyboardInterrupt:
        print("\n⏹️  Scraper interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        
        # Take error screenshot
        if driver:
            try:
                screenshot_path = "output/error_screenshot.png"
                driver.save_screenshot(screenshot_path)
                print(f"   Error screenshot saved: {screenshot_path}")
            except:
                pass
        
        sys.exit(1)
        
    finally:
        if driver:
            print("🔄 Closing browser...")
            close_browser(driver)
        
        print("=" * 60)
        print("🏁 Scraper completed!")

if __name__ == "__main__":
    main()
