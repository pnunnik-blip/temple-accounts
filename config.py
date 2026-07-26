import streamlit as st

# ------------------------------
# Temple Details
# ------------------------------

TEMPLE_NAME = "ഗോവിന്ദപുരം ശ്രീകൃഷ്ണ ക്ഷേത്രം"

APP_TITLE = "Temple Accounts"

CURRENCY = "₹"

DATE_FORMAT = "%Y-%m-%d"

# ------------------------------
# Google Apps Script URL
# ------------------------------

API_URL = st.secrets["API_URL"]

# ------------------------------
# Receipt Settings
# ------------------------------

RECEIPT_PREFIX = "VR"

VOUCHER_PREFIX = "EX"

# ------------------------------
# Payment Modes
# ------------------------------

PAYMENT_MODES = [
    "Cash",
    "UPI",
    "Bank Transfer"
]

# ------------------------------
# Expense Categories
# ------------------------------

EXPENSE_CATEGORIES = [
    "പൂജാ സാധനങ്ങൾ",
    "ശമ്പളം",
    "വൈദ്യുതി / വെള്ളം",
    "അറ്റകുറ്റപ്പണികൾ",
    "മറ്റുള്ളവ"
]