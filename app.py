import streamlit as st
import pandas as pd
from datetime import datetime

# Set up page configurations
st.set_page_config(page_title="Govindapuram Temple Accounts", page_icon="🛕", layout="wide")

# Title of the Application
st.title("🛕 ഗോവിന്ദപുരം ശ്രീകൃഷ്ണ ക്ഷേത്രം - Accounts App")
st.markdown("---")

# 1. Dummy Data Initialization (Replace with your Google Sheet connection if needed)
@st.cache_data
def load_vazhipadu_data():
    # Creating a sample DataFrame for Vazhipadu names and amounts
    data = {
        "name": ["പുഷ്പാഞ്ജലി (Pushpanjali)", "പായസം (Payasam)", "വിളക്ക് (Vilakku)", "നെയ്‌വിളക്ക് (Neyvilakku)"],
        "default_amount": [20.0, 50.0, 30.0, 40.0]
    }
    return pd.DataFrame(data)

vazhipadu_df = load_vazhipadu_data()

# Initialize session states for storing inputs if not using a live database yet
if "vazhipadu_records" not in st.session_state:
    st.session_state.vazhipadu_records = []
if "expense_records" not in st.session_state:
    st.session_state.expense_records = []

# 2. Sidebar Navigation Tabs
menu = ["വഴിപാട് (Vazhipadu)", "ചിലവുകൾ (Expenses)", "റിപ്പോർട്ടുകൾ (Reports)"]
choice = st.sidebar.selectbox("മെനു തിരഞ്ഞെടുക്കുക (Select Menu)", menu)

# --- TAB 1: VAZHIPADU ENTRY ---
if choice == "വഴിപാട് (Vazhipadu)":
    st.header("വഴിപാട് വരവ് ചേർക്കുക (Add Vazhipadu Income)")
    
    with st.form("vazhipadu_form"):
        init_name = st.text_input("പേര് * (Name)")
        init_star = st.text_input("നക്ഷത്രം (Star)")
        
        # Select multiple offerings
        selected_vazhipadus = st.multiselect("വഴിപാടുകൾ തിരഞ്ഞെടുക്കുക (Select Offerings)", vazhipadu_df["name"].tolist())
        
        # FIXED LINE 128: Safe Float calculation to prevent 0-dimensional array errors
        calculated_amt = 0.0
        for item in selected_vazhipadus:
            matching_data = vazhipadu_df[vazhipadu_df["name"] == item]["default_amount"].values
            if len(matching_data) > 0:
                calculated_amt += float(matching_data[0])  # Explicitly extract the first scalar value safely
            else:
                calculated_amt += 0.0

        st.info(f"ആകെ തുക (Calculated Total): ₹{calculated_amt}")
        submit = st.form_submit_with_clicks = st.form_submit_button("ചേർക്കുക (Submit)")
        
        if submit:
            if init_name and selected_vazhipadus:
                new_record = {
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Name": init_name,
                    "Star": init_star if init_star else "N/A",
                    "Offerings": ", ".join(selected_vazhipadus),
                    "Amount": calculated_amt
                }
                st.session_state.vazhipadu_records.append(new_record)
                st.success(f"✅ {init_name} പേരിലുള്ള വഴിപാട് വിജയകരമായി ചേർത്തു!")
            else:
                st.error("⚠️ ദയവായി പേരും വഴിപാടും തിരഞ്ഞെടുക്കുക!")

# --- TAB 2: EXPENSES (Fixed Blank Screen Issue) ---
elif choice == "ചിലവുകൾ (Expenses)":
    st.header("ചിലവുകൾ രേഖപ്പെടുത്തുക (Record Expenses)")
    
    # Securely wrapped block with proper indentation to avoid IndentationError
    try:
        with st.form("expense_form"):
            expense_category = st.selectbox("ചിലവ് ഇനം (Expense Category)", ["പൂജാ സാധനങ്ങൾ", "ശമ്പളം", "വൈദ്യുതി / വെള്ളം", "അറ്റകുറ്റപ്പണികൾ", "മറ്റുള്ളവ"])
            expense_details = st.text_input("വിവരങ്ങൾ (Description)")
            expense_amount = st.number_input("തുക (Amount * )", min_value=0.0, step=10.0)
            expense_submit = st.form_submit_button("ചിലവ് ചേർക്കുക (Save Expense)")
            
            if expense_submit:
                if expense_amount > 0:
                    new_expense = {
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Category": expense_category,
                        "Details": expense_details if expense_details else "N/A",
                        "Amount": expense_amount
                    }
                    st.session_state.expense_records.append(new_expense)
                    st.success("✅ ചിലവ് വിവരങ്ങൾ വിജയകരമായി രേഖപ്പെടുത്തി!")
                else:
                    st.error("⚠️ ദയവായി സാധുവായ ഒരു തുക രേഖപ്പെടുത്തുക!")
                    
    except Exception as e:
        st.error(f"Error handling expense layout: {e}")

    # Display live recorded expenses below the form
    st.subheader("രേഖപ്പെടുത്തിയ ചിലവുകൾ (Recorded Expense List)")
    if st.session_state.expense_records:
        df_exp = pd.DataFrame(st.session_state.expense_records)
        st.dataframe(df_exp, use_container_width=True)
    else:
        st.info("നിലവിൽ ചിലവുകൾ ഒന്നും രേഖപ്പെടുത്തിയിട്ടില്ല.")

# --- TAB 3: REPORTS (Fixed Blank Screen Issue) ---
elif choice == "റിപ്പോർട്ടുകൾ (Reports)":
    st.header("വരവ് ചിലവ് കണക്കുകൾ (Financial Reports)")
    
    col1, col2, col3 = st.columns(3)
    
    total_income = sum(rec["Amount"] for rec in st.session_state.vazhipadu_records)
    total_expense = sum(rec["Amount"] for rec in st.session_state.expense_records)
    net_balance = total_income - total_expense
    
    with col1:
        st.metric(label="ആകെ വരവ് (Total Income)", value=f"₹{total_income}")
    with col2:
        st.metric(label="ആകെ ചിലവ് (Total Expense)", value=f"₹{total_expense}")
    with col3:
        st.metric(label="ബാക്കി നീക്കിയിരിപ്പ് (Balance)", value=f"₹{net_balance}")
        
    st.markdown("---")
    
    st.subheader("വഴിപാട് വരവുകളുടെ വിശദാംശങ്ങൾ (Detailed Income Ledger)")
    if st.session_state.vazhipadu_records:
        st.dataframe(pd.DataFrame(st.session_state.vazhipadu_records), use_container_width=True)
    else:
        st.info("വരവുകൾ ഒന്നും ലഭ്യമല്ല.")
        
    st.subheader("ചിലവുകളുടെ വിശദാംശങ്ങൾ (Detailed Expense Ledger)")
    if st.session_state.expense_records:
        st.dataframe(pd.DataFrame(st.session_state.expense_records), use_container_width=True)
    else:
        st.info("ചിലവുകൾ ഒന്നും ലഭ്യമല്ല.")
