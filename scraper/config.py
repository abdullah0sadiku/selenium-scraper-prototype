import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHROMEDRIVER_PATH = os.path.join(PROJECT_ROOT, "chromedriver.exe")

USE_LOCAL_HTML = False 

# Target frontend URLs
LOGIN_URL = "http://localhost:28318/login"
DASHBOARD_URL = "http://localhost:28318/homepage1"  # or homepage2, depending on the default

# dictionary of test users for login; can be expanded
TEST_USERS = {
    "john.doe@email.com": "password123",
    "jane.smith@email.com": "test456",
    "admin@bank.com": "admin789",
}

# default user for automated scraper login; change as needed
DEFAULT_USERNAME = "john.doe@email.com"
DEFAULT_PASSWORD = TEST_USERS[DEFAULT_USERNAME]

# Login form selectors (from React code)
USERNAME_SELECTOR = 'input#email'
PASSWORD_SELECTOR = 'input#password'
LOGIN_BUTTON_SELECTOR = 'button[type="submit"]'

# Login success check, something unique that appears only post-login
POST_LOGIN_SUCCESS_SELECTOR = 'h1.text-2xl.font-semibold'

# # Transaction table (could be list or table depending on implementation)
# TRANSACTION_ROW_SELECTOR = 'div[data-testid="transaction-row"]'
# TRANSACTION_FIELDS = {
#     "date": 'div[data-testid="transaction-date"]',
#     "vendor": 'div[data-testid="transaction-vendor"]',
#     "category": 'div[data-testid="transaction-category"]',
#     "amount": 'div[data-testid="transaction-amount"]',
# }

# === Transaction Extract Selectors ===

# homepage1 layout (div-based structure)
HOMEPAGE1_CONTAINER_SELECTOR = 'div[class*="shadow-neumorphism"]'
HOMEPAGE1_ROW_SELECTOR = 'div[id^="transaction-"][id$="-name"]'
HOMEPAGE1_FIELD_MAP = {
    'name': lambda id: f'div#{id}-name',
    'amount': lambda id: f'div#{id}-amount',
    'date': lambda id: f'div#{id}-date',
}

# homepage2 layout (ul/li structure)
HOMEPAGE2_ITEM_SELECTOR = 'ul li'
HOMEPAGE2_FIELD_CLASSES = {
    'name': 'font-bold',
    'merchant': 'text-gray-400',
    'amount': 'text-right',
}


# Output files
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
CSV_PATH = os.path.join(OUTPUT_DIR, "transactions.csv")
PARQUET_PATH = os.path.join(OUTPUT_DIR, "transactions.parquet")
SCREENSHOT_PATH = os.path.join(OUTPUT_DIR, "dashboard.png")
HTML_DUMP_PATH = os.path.join(OUTPUT_DIR, "page_source.html")