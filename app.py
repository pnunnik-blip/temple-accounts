import streamlit as st

from pages import income
from pages import expenses
from pages import reports
from pages import dashboard
from pages import settings


# -------------------------------------
# Page Configuration
# -------------------------------------

st.set_page_config(
    page_title="Govindapuram Temple Accounts",
    page_icon="🛕",
    layout="wide"
)


# -------------------------------------
# Header
# -------------------------------------

st.title("🛕 ഗോവിന്ദപുരം ശ്രീകൃഷ്ണ ക്ഷേത്രം")
st.subheader("Temple Accounts Management System")

st.markdown("---")


# -------------------------------------
# Navigation Menu
# -------------------------------------

menu = [

    "Dashboard",
    "വഴിപാട് വരവ് (Income)",
    "ചിലവുകൾ (Expenses)",
    "റിപ്പോർട്ടുകൾ (Reports)",
    "Settings"

]


choice = st.sidebar.selectbox(
    "Menu",
    menu
)


# -------------------------------------
# Page Routing
# -------------------------------------

if choice == "Dashboard":

    dashboard.show()


elif choice == "വഴിപാട് വരവ് (Income)":

    income.show()


elif choice == "ചിലവുകൾ (Expenses)":

    expenses.show()


elif choice == "റിപ്പോർട്ടുകൾ (Reports)":

    reports.show()


elif choice == "Settings":

    settings.show()