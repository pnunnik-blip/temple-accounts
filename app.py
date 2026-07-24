import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def get_db_connection():
    conn = sqlite3.connect("temple_final_v10.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date TEXT, record_time TEXT, booking_date TEXT, income_type TEXT, 
            devotee_name TEXT, star TEXT, house_name TEXT, 
            phone_number TEXT, vazhipadu_items TEXT, amount REAL, 
            payment_mode TEXT, payment_status TEXT, remarks TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, expense_category TEXT, item_detail TEXT, 
            amount REAL, payment_mode TEXT, remarks TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vazhipadu_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE, default_amount REAL
        )
    """)
    default_vazhipadus = [
        ("അർച്ചന", 20.0), ("പുഷ്പാഞ്ജലി", 30.0), ("നെയ്‌വിളക്ക്", 50.0), 
        ("ഗണപതി ഹോമം", 150.0), ("പാല്പായസം", 100.0)
    ]
    for name, amt in default_vazhipadus:
        try:
            cursor.execute("INSERT INTO vazhipadu_master (name, default_amount) VALUES (?, ?)", (name, amt))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

init_db()

def get_existing_devotees():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT DISTINCT devotee_name, star, house_name, phone_number FROM income WHERE devotee_name != 'ഭണ്ടാരം വരവ്'", conn)
    conn.close()
    return df

def get_existing_expenses():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT DISTINCT item_detail, expense_category FROM expenses", conn)
    conn.close()
    return df

def get_vazhipadu_list():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT name, default_amount FROM vazhipadu_master ORDER BY name ASC", conn)
    conn.close()
    return df

st.set_page_config(page_title="ഗോന്ദപുരം ശ്രീകൃഷ്ണ ക്ഷേത്രം", layout="wide")
st.markdown("<h2 style='text-align: center; color: #E65100;'>🛕 ഗോന്ദപുരം ശ്രീകൃഷ്ണ ക്ഷേത്രം</h2>", unsafe_style=True)
st.markdown("<h4 style='text-align: center; color: #555;'>പാറക്കാട്ടുകര, 680683</h4>", unsafe_style=True)

menu = ["📊 ഡാഷ്‌ബോർഡ്", "💰 വരവുകൾ (Income)", "⚙️ വഴിപാട് ലിസ്റ്റ് ക്രമീകരണം", "🔔 ഓർമ്മപ്പെടുത്തലുകൾ", "📉 ചിലവുകൾ (Expenses)", "📜 റിപ്പോർട്ടുകൾ"]
choice = st.sidebar.selectbox("മെനു", menu)

if choice == "📊 ഡാഷ്‌ബോർഡ്":
    st.subheader("സാമ്പത്തിക സ്ഥിതിവിവരക്കണക്കുകൾ")
    conn = get_db_connection()
    cash_inc = pd.read_sql_query("SELECT amount FROM income WHERE payment_status = 'പണം ലഭിച്ചു (Paid)' AND payment_mode = 'Cash'", conn)["amount"].sum()
    upi_inc = pd.read_sql_query("SELECT amount FROM income WHERE payment_status = 'പണം ലഭിച്ചു (Paid)' AND payment_mode = 'UPI / Bank'", conn)["amount"].sum()
    cash_exp = pd.read_sql_query("SELECT amount FROM expenses WHERE payment_mode = 'Cash'", conn)["amount"].sum()
    upi_exp = pd.read_sql_query("SELECT amount FROM expenses WHERE payment_mode = 'UPI / Bank'", conn)["amount"].sum()
    total_pending = pd.read_sql_query("SELECT amount FROM income WHERE payment_status = 'പിന്നീട് തരും (Pending)'", conn)["amount"].sum()
    
    cash_in_hand = cash_inc - cash_exp
    upi_balance = upi_inc - upi_exp
    total_balance = cash_in_hand + upi_balance
    
    col1, col2, col3 = st.columns(3)
    col1.metric("💵 കയ്യിലുള്ള പണം", f"₹{cash_in_hand:,.2f}")
    col2.metric("📱  ബാങ്ക് / UPI തുക", f"₹{upi_balance:,.2f}")
    col3.metric("🏛️ ആകെ ബാക്കി", f"₹{total_balance:,.2f}")
    st.markdown("---")
    if total_pending > 0:
        st.warning(f"⚠️ കിട്ടാനുള്ള തുക (Pending): ₹{total_pending:,.2f}")
    conn.close()

elif choice == "💰 വരവുകൾ (Income)":
    st.subheader("വരവുകൾ / വഴിപാട് ബുക്കിംഗ്")
    income_type = st.radio("ഇനം:", ["വഴിപാട്", "സംഭാവന", "ഭണ്ടാരം (മാസത്തിൽ എടുക്കുന്നത്)"])
    devotees_df = get_existing_devotees()
    vazhipadu_df = get_vazhipadu_list()
    
    existing_names = ["-- പുതിയ ഭക്തൻ (New Devotee) --"] + devotees_df["devotee_name"].tolist()
    selected_name_option = "-- പുതിയ ഭക്തൻ (New Devotee) --"
    if income_type in ["വഴിപാട്", "സംഭാവന"] and len(existing_names) > 1:
        selected_name_option = st.selectbox("മുൻപ് വന്നിട്ടുള്ള ആളാണെങ്കിൽ പേര് തിരഞ്ഞെടുക്കുക:", existing_names)
    
    init_name, init_star, init_house, init_phone = "", "", "", ""
    if selected_name_option != "-- പുതിയ ഭക്തൻ (New Devotee) --":
        matched_user = devotees_df[devotees_df["devotee_name"] == selected_name_option].iloc
        init_name = matched_user["devotee_name"]
        init_star = matched_user["star"]
        init_house = matched_user["house_name"]
        init_phone = matched_user["phone_number"]

    with st.form("income_form", clear_on_submit=True):
        col_d1, col_t1 = st.columns(2)
        with col_d1:
            record_date = st.date_input("രേഖപ്പെടുത്തുന്ന തീയതി", datetime.now())
        with col_t1:
            record_time = st.time_input("സമയം", datetime.now().time())
        
        if income_type == "വഴിപാട്":
            booking_date = st.date_input("വഴിപാട് നടത്തുന്ന തീയതി")
            selected_vazhipadus = st.multiselect("വഴിപാട് ഇനങ്ങൾ തിരഞ്ഞെടുക്കുക (ഒന്നിലധികം ആകാം):", vazhipadu_df["name"].tolist())
            
            calculated_amt = 0.0
            for item in selected_vazhipadus:
                calculated_amt += float(vazhipadu_df[vazhipadu_df["name"] == item]["default_amount"].values)
       
