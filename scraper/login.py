import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from scraper.config import DEFAULT_USERNAME, DEFAULT_PASSWORD, SCREENSHOT_PATH, LOGIN_URL, DASHBOARD_URL

def is_real_dashboard_content(driver):
    """
    Check if we have real dashboard content (not login form).
    Based on BankDashboard repo, look for actual financial content.
    """
    try:
        # Check for login form elements (bad sign)
        login_indicators = [
            "input#email",
            "input#password", 
            "button[type='submit']",
            "//*[contains(text(), 'Email Address')]",
            "//*[contains(text(), 'Password')]",
            "//*[contains(text(), 'Remember me')]",
            "//*[contains(text(), 'Forgot password')]"
        ]
        
        for indicator in login_indicators:
            try:
                if indicator.startswith('//'):
                    elements = driver.find_elements(By.XPATH, indicator)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, indicator)
                
                if elements:
                    print(f"[login] Still seeing login element: {indicator}")
                    return False
            except:
                continue
        
        # Check for real dashboard content (good signs)
        dashboard_indicators = [
            # Financial content
            "//*[contains(text(), '$') and not(contains(text(), 'Email')) and not(contains(text(), 'Password'))]",
            "//*[contains(text(), 'Balance') and not(contains(text(), 'Email'))]",
            "//*[contains(text(), 'Transaction') and not(contains(text(), 'Email'))]",
            "//*[contains(text(), 'Income')]",
            "//*[contains(text(), 'Expense')]",
            "//*[contains(text(), 'Transfer')]",
            # Dashboard elements
            "nav:not(:has(input))",  # Navigation without login inputs
            "[class*='transaction']:not(:has(input))",
            "[class*='balance']:not(:has(input))",
            "[class*='card']:not(:has(input))",
            "[data-testid*='transaction']",
            "[data-testid*='balance']"
        ]
        
        dashboard_content_found = 0
        for indicator in dashboard_indicators:
            try:
                if indicator.startswith('//'):
                    elements = driver.find_elements(By.XPATH, indicator)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, indicator)
                
                if elements:
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 3:
                            dashboard_content_found += 1
                            print(f"[login] Found dashboard content: {text[:50]}...")
                            break
            except:
                continue
        
        # Need at least 2 dashboard indicators and no login indicators
        is_dashboard = dashboard_content_found >= 2
        print(f"[login] Dashboard content score: {dashboard_content_found}/2 required")
        return is_dashboard
        
    except Exception as e:
        print(f"[login] Error checking dashboard content: {e}")
        return False

def spam_login_until_success(driver, max_attempts=10, timeout_per_attempt=3):
    """
    Aggressively spam login attempts until we get real dashboard content.
    """
    print(f"[login] Starting aggressive login spamming (max {max_attempts} attempts)")
    
    for attempt in range(max_attempts):
        print(f"\n[login] === ATTEMPT {attempt + 1}/{max_attempts} ===")
        
        # Check if we already have dashboard content
        if is_real_dashboard_content(driver):
            print(f"[login] SUCCESS! Real dashboard detected on attempt {attempt + 1}")
            return True
        
        # Navigate to dashboard route if not already there
        current_url = driver.current_url
        if "homepage1" not in current_url and "homepage2" not in current_url:
            print(f"[login] Navigating to dashboard: {DASHBOARD_URL}")
            driver.get(DASHBOARD_URL)
            time.sleep(1)
        
        # Look for login form and fill it aggressively
        try:
            # Try to find login form elements
            email_field = None
            password_field = None
            remember_me_checkbox = None
            submit_button = None
            
            # Multiple ways to find email field
            for selector in ["input#email", "input[type='email']", "input[name='email']", "input[placeholder*='email']"]:
                try:
                    email_field = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            # Multiple ways to find password field
            for selector in ["input#password", "input[type='password']", "input[name='password']"]:
                try:
                    password_field = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            # Multiple ways to find remember me checkbox
            for selector in [
                "input[type='checkbox']",
                "input[name='remember']", 
                "input[name='rememberMe']",
                "input[id*='remember']",
                "input[class*='remember']",
                "//*[contains(text(), 'Remember') or contains(text(), 'remember')]/preceding-sibling::input[@type='checkbox']",
                "//*[contains(text(), 'Remember') or contains(text(), 'remember')]/following-sibling::input[@type='checkbox']"
            ]:
                try:
                    if selector.startswith('//'):
                        remember_me_checkbox = driver.find_element(By.XPATH, selector)
                    else:
                        remember_me_checkbox = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            # Multiple ways to find submit button
            for selector in ["button[type='submit']", "input[type='submit']", "button:contains('Sign')", "button:contains('Login')"]:
                try:
                    submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if email_field and password_field and submit_button:
                print(f"[login] Found login form, filling credentials...")
                
                # Clear and fill aggressively
                email_field.clear()
                email_field.send_keys(DEFAULT_USERNAME)
                
                password_field.clear()
                password_field.send_keys(DEFAULT_PASSWORD)
                
                # Check "Remember me" if found
                if remember_me_checkbox:
                    try:
                        if not remember_me_checkbox.is_selected():
                            print("[login] Checking 'Remember me' checkbox...")
                            remember_me_checkbox.click()
                            print("[login] ✅ 'Remember me' checkbox checked!")
                        else:
                            print("[login] 'Remember me' already checked")
                    except Exception as e:
                        print(f"[login] Could not check 'Remember me': {e}")
                        # Try JavaScript click as fallback
                        try:
                            driver.execute_script("arguments[0].checked = true;", remember_me_checkbox)
                            print("[login] ✅ 'Remember me' set via JavaScript!")
                        except:
                            print("[login] JavaScript checkbox check also failed")
                else:
                    print("[login] No 'Remember me' checkbox found")
                
                # Multiple click strategies
                try:
                    # Strategy 1: Regular click
                    submit_button.click()
                    print("[login] Regular click executed")
                except:
                    try:
                        # Strategy 2: JavaScript click
                        driver.execute_script("arguments[0].click();", submit_button)
                        print("[login] JavaScript click executed")
                    except:
                        try:
                            # Strategy 3: Send Enter key
                            password_field.send_keys(Keys.ENTER)
                            print("[login] Enter key sent")
                        except:
                            print("[login] All click strategies failed")
                
                # Wait for processing without refreshing
                print("[login] Waiting for React state to update...")
                time.sleep(timeout_per_attempt)
                
            else:
                print(f"[login] Login form not found or incomplete")
                print(f"  Email field: {'Found' if email_field else 'Missing'}")
                print(f"  Password field: {'Found' if password_field else 'Missing'}")
                print(f"  Submit button: {'Found' if submit_button else 'Missing'}")
                print(f"  Remember me: {'Found' if remember_me_checkbox else 'Missing'}")
                
                # Wait a bit before next attempt without refreshing
                time.sleep(1)
                
        except Exception as e:
            print(f"[login] Error in attempt {attempt + 1}: {e}")
            # Continue to next attempt
            time.sleep(1)
    
    print(f"[login] FAILED after {max_attempts} attempts")
    return False

def perform_login(driver, timeout=30):
    """
    Main login function that uses aggressive spamming approach.
    """
    print("[login] Starting aggressive login process...")
    
    # Step 1: Try initial login from login page
    print(f"[login] Step 1: Initial login attempt from {LOGIN_URL}")
    try:
        driver.get(LOGIN_URL)
        time.sleep(2)
        
        # Try one normal login first
        email_field = driver.find_element(By.CSS_SELECTOR, "input#email")
        password_field = driver.find_element(By.CSS_SELECTOR, "input#password")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # Look for remember me checkbox
        remember_me_checkbox = None
        for selector in [
            "input[type='checkbox']",
            "input[name='remember']", 
            "input[name='rememberMe']",
            "input[id*='remember']",
            "input[class*='remember']"
        ]:
            try:
                remember_me_checkbox = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        email_field.clear()
        email_field.send_keys(DEFAULT_USERNAME)
        password_field.clear()
        password_field.send_keys(DEFAULT_PASSWORD)
        
        # Check "Remember me" if found
        if remember_me_checkbox:
            try:
                if not remember_me_checkbox.is_selected():
                    print("[login] Checking 'Remember me' checkbox in initial login...")
                    remember_me_checkbox.click()
                    print("[login] ✅ 'Remember me' checkbox checked!")
                else:
                    print("[login] 'Remember me' already checked")
            except Exception as e:
                print(f"[login] Could not check 'Remember me': {e}")
                # Try JavaScript click as fallback
                try:
                    driver.execute_script("arguments[0].checked = true;", remember_me_checkbox)
                    print("[login] ✅ 'Remember me' set via JavaScript!")
                except:
                    print("[login] JavaScript checkbox check also failed")
        else:
            print("[login] No 'Remember me' checkbox found in initial login")
        
        submit_button.click()
        
        time.sleep(3)
        print("[login] Initial login attempt completed")
        
    except Exception as e:
        print(f"[login] Initial login failed: {e}")
    
    # Step 2: Navigate to dashboard and start spamming
    print(f"[login] Step 2: Navigating to dashboard and starting spam login")
    driver.get(DASHBOARD_URL)
    time.sleep(2)
    
    # Step 3: Spam login until success
    success = spam_login_until_success(driver, max_attempts=15, timeout_per_attempt=3)
    
    if success:
        print("[login] 🎉 LOGIN SUCCESSFUL! Real dashboard content detected")
    else:
        print("[login] ❌ LOGIN FAILED after all attempts")
        print("[login] Trying localStorage injection as final fallback...")
        
        # Final fallback: localStorage injection with persistent session
        driver.execute_script(f"""
            localStorage.clear();
            sessionStorage.clear();
            
            const userData = {{
                email: "{DEFAULT_USERNAME}",
                name: "{DEFAULT_USERNAME.split('@')[0].replace('.', ' ').title()}",
                authenticated: true,
                isLoggedIn: true,
                token: "demo-token-12345",
                rememberMe: true,
                sessionPersistent: true
            }};
            
            localStorage.setItem('user', JSON.stringify(userData));
            localStorage.setItem('isAuthenticated', 'true');
            localStorage.setItem('authToken', 'demo-token-12345');
            localStorage.setItem('loginStatus', 'success');
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('rememberMe', 'true');
            localStorage.setItem('sessionPersistent', 'true');
            
            sessionStorage.setItem('isAuthenticated', 'true');
            sessionStorage.setItem('authToken', 'demo-token-12345');
            sessionStorage.setItem('user', JSON.stringify(userData));
            sessionStorage.setItem('isLoggedIn', 'true');
            sessionStorage.setItem('rememberMe', 'true');
            
            // Set cookies for additional persistence
            document.cookie = 'isAuthenticated=true; path=/; max-age=86400';
            document.cookie = 'authToken=demo-token-12345; path=/; max-age=86400';
            document.cookie = 'rememberMe=true; path=/; max-age=86400';
            
            console.log('Comprehensive authentication state with Remember Me injected');
        """)
        
        driver.refresh()
        time.sleep(5)
        
        if is_real_dashboard_content(driver):
            print("[login] 🎉 SUCCESS with localStorage injection!")
        else:
            print("[login] ❌ All methods failed")
    
    # Take final screenshot
    print(f"[login] Taking screenshot: {SCREENSHOT_PATH}")
    driver.save_screenshot(SCREENSHOT_PATH)
    
    print("→ Current URL:", driver.current_url)
    print("→ Page Title:", driver.title)
    print("→ User in localStorage:", driver.execute_script("return window.localStorage.getItem('user');"))
    print("→ Remember Me status:", driver.execute_script("return window.localStorage.getItem('rememberMe');"))