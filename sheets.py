import requests
import pandas as pd
from config import API_URL


# ============================================
# Helper function to call Google Apps Script
# ============================================

def call_api(action, data=None):
    """
    Sends a request to Google Apps Script.

    Parameters:
        action : save_income, save_expense,
                 get_income, get_expenses,
                 get_vazhipadu

        data : dictionary (optional)
    """

    payload = {
        "action": action,
        "data": data
    }

    try:

        response = requests.post(
            API_URL,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:

            return response.json()

        else:

            return {
                "status": "error",
                "message": f"HTTP Error {response.status_code}"
            }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# ============================================
# Income
# ============================================

def save_income(record):

    return call_api(
        "save_income",
        record
    )


def get_income():

    return call_api(
        "get_income"
    )


# ============================================
# Expenses
# ============================================

def save_expense(record):

    return call_api(
        "save_expense",
        record
    )


def get_expenses():

    return call_api(
        "get_expenses"
    )


# ============================================
# Vazhipadu Master
# ============================================

def get_vazhipadu_master():

    return call_api(
        "get_vazhipadu"
    )