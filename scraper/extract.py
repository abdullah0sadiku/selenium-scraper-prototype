# handles data scraping logic
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def extract_transactions(driver, timeout=10):
    """
    Extract transactions from the BankDashboard application.
    This function tries multiple approaches to find transaction data.
    """
    print("[extract] Starting transaction extraction...")
    
    # Wait a moment for any dynamic content to load
    time.sleep(2)
    
    # Try different extraction methods based on the BankDashboard structure
    transactions = []
    
    # Method 1: Look for transaction cards/items
    transactions = _extract_transaction_cards(driver)
    if transactions:
        print(f"[extract] Found {len(transactions)} transactions using card method")
        return transactions
    
    # Method 2: Look for table-based transactions
    transactions = _extract_transaction_table(driver)
    if transactions:
        print(f"[extract] Found {len(transactions)} transactions using table method")
        return transactions
    
    # Method 3: Look for list-based transactions
    transactions = _extract_transaction_list(driver)
    if transactions:
        print(f"[extract] Found {len(transactions)} transactions using list method")
        return transactions
    
    # Method 4: Generic approach - look for any elements with transaction-like content
    transactions = _extract_generic_transactions(driver)
    if transactions:
        print(f"[extract] Found {len(transactions)} transactions using generic method")
        return transactions
    
    print("[extract] No transactions found with any method")
    _debug_page_content(driver)
    raise Exception("No known transaction layout found.")

def _extract_transaction_cards(driver):
    """
    Extract transactions from card-based layout (common in modern dashboards).
    """
    transactions = []
    
    # Look for transaction cards - prioritize transaction-specific selectors
    card_selectors = [
        'div[class*="transaction"]',
        'div[data-testid*="transaction"]',
        '.transaction-card',
        '.transaction-item',
        'div[class*="card"]:not([class*="login"])',  # Exclude login cards
        'div[class*="item"]:not([class*="login"])'   # Exclude login items
    ]
    
    for selector in card_selectors:
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, selector)
            if cards:
                print(f"[extract] Found {len(cards)} cards with selector: {selector}")
                
                for card in cards:
                    transaction = _extract_from_element(card)
                    if transaction and _is_valid_transaction(transaction):
                        transactions.append(transaction)
                
                if transactions:
                    return transactions
        except Exception as e:
            print(f"[extract] Error with selector {selector}: {e}")
            continue
    
    return transactions

def _extract_transaction_table(driver):
    """
    Extract transactions from table-based layout.
    """
    transactions = []
    
    try:
        # Look for table rows
        rows = driver.find_elements(By.CSS_SELECTOR, "table tr, tbody tr")
        if len(rows) > 1:  # Skip header row
            print(f"[extract] Found {len(rows)} table rows")
            
            for row in rows[1:]:  # Skip header
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                if len(cells) >= 2:
                    transaction = {
                        "description": cells[0].text.strip() if len(cells) > 0 else "",
                        "amount": cells[1].text.strip() if len(cells) > 1 else "",
                        "date": cells[2].text.strip() if len(cells) > 2 else "",
                        "category": cells[3].text.strip() if len(cells) > 3 else ""
                    }
                    
                    if _is_valid_transaction(transaction):
                        transactions.append(transaction)
    except Exception as e:
        print(f"[extract] Error extracting table: {e}")
    
    return transactions

def _extract_transaction_list(driver):
    """
    Extract transactions from list-based layout.
    """
    transactions = []
    
    try:
        # Look for list items that might contain transactions
        items = driver.find_elements(By.CSS_SELECTOR, "ul li, ol li")
        if items:
            print(f"[extract] Found {len(items)} list items")
            
            for item in items:
                transaction = _extract_from_element(item)
                if transaction and _is_valid_transaction(transaction):
                    transactions.append(transaction)
    except Exception as e:
        print(f"[extract] Error extracting list: {e}")
    
    return transactions

def _extract_generic_transactions(driver):
    """
    Generic extraction method that looks for any elements containing transaction-like data.
    """
    transactions = []
    
    try:
        # Look for any elements containing money amounts
        money_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '$') or contains(text(), '€') or contains(text(), '£') or contains(text(), 'USD') or contains(text(), 'EUR')]")
        
        print(f"[extract] Found {len(money_elements)} elements with money symbols")
        
        for element in money_elements:
            # Try to find the parent container that might have the full transaction
            try:
                parent = element.find_element(By.XPATH, "..")
                transaction = _extract_from_element(parent)
                
                if transaction and _is_valid_transaction(transaction) and transaction not in transactions:
                    transactions.append(transaction)
            except:
                continue
                
    except Exception as e:
        print(f"[extract] Error in generic extraction: {e}")
    
    return transactions

def _extract_from_element(element):
    """
    Extract transaction data from a single element.
    """
    try:
        text = element.text.strip()
        if not text:
            return None
        
        # Look for amount patterns (more comprehensive)
        import re
        amount_pattern = r'[\$€£]?\s*[\d,]+\.?\d*|[\d,]+\.?\d*\s*[\$€£USD EUR]'
        amounts = re.findall(amount_pattern, text)
        
        # Look for date patterns
        date_pattern = r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}|\w{3}\s+\d{1,2},?\s+\d{4}'
        dates = re.findall(date_pattern, text)
        
        # Extract the first line as description
        lines = text.split('\n')
        description = lines[0] if lines else text
        
        transaction = {
            "description": description,
            "amount": amounts[0] if amounts else "",
            "date": dates[0] if dates else "",
            "full_text": text
        }
        
        # Only return if we have meaningful data
        if transaction["description"] and len(transaction["description"]) > 2:
            return transaction
            
    except Exception as e:
        print(f"[extract] Error extracting from element: {e}")
    
    return None

def _is_valid_transaction(transaction):
    """
    Check if the extracted transaction is valid and not a login form element.
    """
    if not transaction or not transaction.get("description"):
        return False
    
    description = transaction["description"].lower()
    full_text = transaction.get("full_text", "").lower()
    
    # Filter out login form elements
    login_keywords = [
        "remember me", "forgot password", "login", "sign in", "email", "password",
        "username", "submit", "welcome back", "securbank", "dashboard"
    ]
    
    # Check if this looks like a login form element
    for keyword in login_keywords:
        if keyword in description or keyword in full_text:
            return False
    
    # Must have some meaningful content
    if len(description) < 3:
        return False
    
    # Prefer transactions with amounts or dates
    has_amount = transaction.get("amount") and len(transaction["amount"]) > 0
    has_date = transaction.get("date") and len(transaction["date"]) > 0
    has_money_symbol = any(symbol in full_text for symbol in ['$', '€', '£', 'USD', 'EUR'])
    
    # Accept if it has financial indicators or is substantial content
    return has_amount or has_date or has_money_symbol or len(description) > 10

def _debug_page_content(driver):
    """
    Debug function to print page content when no transactions are found.
    """
    print("\n[extract] DEBUG: Page content analysis")
    print(f"Current URL: {driver.current_url}")
    print(f"Page title: {driver.title}")
    
    # Check for common elements
    elements_to_check = [
        ("divs", "div"),
        ("spans", "span"),
        ("paragraphs", "p"),
        ("lists", "ul, ol"),
        ("tables", "table"),
        ("cards", "[class*='card']"),
        ("transactions", "[class*='transaction']")
    ]
    
    for name, selector in elements_to_check:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"  {name}: {len(elements)} found")
            
            # Show first few elements with text
            for i, elem in enumerate(elements[:3]):
                text = elem.text.strip()[:100]
                if text:
                    print(f"    [{i}] {text}...")
        except:
            pass
    
    print("=" * 50)
