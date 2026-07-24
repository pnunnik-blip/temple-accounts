import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def get_db_connection():
    conn = sqlite3.connect("temple_final_v12.db", check_same_thread=False)
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
        ("ഗണပതി ഹോമം", 150.0), ("പാല്പായസം", 100.0)
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

st.set_page_config(page_title="ഗോവിന്ദപുരം ശ്രീകൃഷ്ണ ക്ഷേത്രം", layout="wide")
st.markdown("<h2 style='text-align: center; color: #E65100;'>🛕 ഗോവിന്ദപുരം ശ്രീകൃഷ്ണ ക്ഷേത്രം</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>പാറക്കാട്ടുകര, 680683</h4>", unsafe_allow_html=True)

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
        matched_user = devotees_df[devotees_df["devotee_name"] == selected_name_option].iloc[0]
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
                calculated_amt += float(vazhipadu_df[vazhipadu_df["name"] == item]["default_amount"].values[0])
            
            name = st.text_input("പേര് *", value=init_name)
            star = st.text_input("നക്ഷത്രം", value=init_star)
            house_name = st.text_input("വീട്ടു പേര്", value=init_house)
            phone = st.text_input("ഫോൺ നമ്പർ", value=init_phone)
            
            amount = st.number_input("ആകെ തുക (₹) * (ആവശ്യമെങ്കിൽ തിരുത്താം)", min_value=0.0, value=calculated_amt, step=5.0)
            mode = st.selectbox("Payment Mode", ["Cash", "UPI / Bank"])
            status = st.selectbox("Payment Status", ["പണം ലഭിച്ചു (Paid)", "പിന്നീട് തരും (Pending)"])
            remarks = st.text_area("കൂടുതൽ വിവരങ്ങൾ")
            vazhipadu_str = ", ".join(selected_vazhipadus)
            
        elif income_type == "സംഭാവന":
            booking_date = record_date
            vazhipadu_str = "സംഭാവന"
            name = st.text_input("പേര് *", value=init_name)
            star = st.text_input("നക്ഷത്രം", value=init_star)
            house_name = st.text_input("വീട്ടു പേര്", value=init_house)
            phone = st.text_input("ഫോൺ നമ്പർ", value=init_phone)
            amount = st.number_input("തുക (₹) *", min_value=1.0, step=50.0)
            mode = st.selectbox("Payment Mode", ["Cash", "UPI / Bank"])
            status = st.selectbox("Payment Status", ["പണം ലഭിച്ചു (Paid)", "പിന്നീട് തരും (Pending)"])
            remarks = st.text_area("കൂടുതൽ വിവരങ്ങൾ")
            
        else:
            booking_date = record_date
            vazhipadu_str = "ഭണ്ടാരം വരവ്"
            name, star, house_name, phone = "ഭണ്ടാരം വരവ്", "-", "-", "-"
            amount = st.number_input("ലഭിച്ച തുക (₹) *", min_value=1.0, step=50.0)
            mode = st.selectbox("പണം ലഭിച്ച രീതി", ["Cash", "UPI / Bank"])
            status = "പണം ലഭിച്ചു (Paid)"
            remarks = st.text_area("വിവരങ്ങൾ")
            
        submit_btn = st.form_submit_button("സേവ് ചെയ്യുക & പ്രിന്റ് ബിൽ")
        if submit_btn:
            if amount > 0 and (income_type == "ഭണ്ടാരം (മാസത്തിൽ എടുക്കുന്നത്)" or name):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO income (record_date, record_time, booking_date, income_type, devotee_name, star, house_name, phone_number, vazhipadu_items, amount, payment_mode, payment_status, remarks) 
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (str(record_date), str(record_time), str(booking_date), income_type, name, star, house_name, phone, vazhipadu_str, amount, mode, status, remarks))
                conn.commit()
                conn.close()
                st.success("വിവരങ്ങൾ വിജയകരമായി രേഖപ്പെടുത്തി!")
                
                if income_type != "ഭണ്ടാരം (മാസത്തിൽ എടുക്കുന്നത്)":
                    st.markdown("---")
                    st.markdown("### 🛕 **ഗോവിന്ദപുരം ശ്രീകൃഷ്ണ ക്ഷേത്രം, പാറക്കാട്ടുകര**")
                    st.write(f"**തീയതി:** {record_date} | **സമയം:** {record_time.strftime('%I:%M %p')}")
                    st.markdown("---")
                    st.write(f"**പേര്:** {name} | **നക്ഷത്രം:** {star}")
                    st.write(f"**വീട്ടു പേര്:** {house_name} | **ഫോൺ:** {phone}")
                    st.write(f"**വഴിപാട് ഇനം:** {vazhipadu_str}")
                    st.write(f"**വഴിപാട് തീയതി:** {booking_date}")
                    st.write(f"**തുക:** ₹{amount:,.2f} ({mode})")
                    st.markdown("*ഹരേ കൃഷ്ണ ! സർവ്വത്ര ഗോവിന്ദ നാമ സങ്കീർത്തനം*")
                    st.markdown("---")
                st.rerun()

elif choice == "⚙️ വഴിപാട് ലിസ്റ്റ് ക്രമീകരണം":
    st.subheader("🗂️ വഴിപാടുകളുടെ ലിസ്റ്റ് മാനേജ് ചെയ്യുക")
    with st.form("new_vazhipadu_form"):
        new_vazhipadu_name = st.text_input("വഴിപാടിന്റെ പേര് *")
        new_vazhipadu_amount = st.number_input("ഡിഫോൾട്ട് നിരക്ക് (₹) *", min_value=0.0, step=5.0)
        add_btn = st.form_submit_button("ലിസ്റ്റിലേക്ക് ചേർക്കുക")
        if add_btn and new_vazhipadu_name:
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO vazhipadu_master (name, default_amount) VALUES (?, ?)", (new_vazhipadu_name, new_vazhipadu_amount))
