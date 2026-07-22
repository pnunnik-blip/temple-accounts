if add_btn and new_vazhipadu_name:
conn = get_db_connection()
cursor = conn.cursor()
try:
cursor.execute("INSERT INTO vazhipadu_master (name, default_amount) VALUES (?, ?)", (new_vazhipadu_name, new_vazhipadu_amount))
conn.commit()
st.success("പുതിയ വഴിപാട് ലിസ്റ്റിൽ ചേർത്തു!")
except sqlite3.IntegrityError:
st.error("ഈ വഴിപാട് നിലവിൽ ലിസ്റ്റിലുണ്ട്!")
conn.close()
st.rerun()
st.markdown("---")
st.markdown("#### 📋 നിലവിലുള്ള വഴിപാടുകളുടെ നിരക്കുകൾ")
v_df = get_vazhipadu_list()
st.dataframe(v_df, use_container_width=True)
elif choice == "🔔 ഓർമ്മപ്പെടുത്തലുകൾ":
st.subheader("📅 നാളത്തെ വഴിപാടുകൾ")
tomorrow_str = str((datetime.now() + timedelta(days=1)).date())
conn = get_db_connection()
reminders_df = pd.read_sql_query(f"SELECT booking_date as 'തീയതി', devotee_name as 'പേര്', vazhipadu_items as 'വഴിപാടുകൾ', star as 'നക്ഷത്രം', phone_number as 'ഫോൺ', amount as 'തുക (₹)', payment_status as 'സ്റ്റാറ്റസ്' FROM income WHERE booking_date = '{tomorrow_str}' AND income_type = 'വഴിപാട്'", conn)
if not reminders_df.empty:
st.dataframe(reminders_df, use_container_width=True)
else:
st.success("🎉 നാളെ പ്രത്യേക വഴിപാട് ബുക്കിംഗുകൾ ഒന്നും തന്നെയില്ല.")
conn.close()
elif choice == "📉 ചിലവുകൾ (Expenses)":
st.subheader("ചിലവുകൾ രേഖപ്പെടുത്തുക")
exp_history_df = get_existing_expenses()
existing_vendors = ["-- പുതിയ ചിലവ് / പുതിയ കട (New Expense) --"] + exp_history_df["item_detail"].tolist()
selected_vendor = st.selectbox("മുൻപ് പണം നൽകിയിട്ടുള്ള കടയോ വ്യക്തിയോ ആണെങ്കിൽ തിരഞ്ഞെടുക്കുക:", existing_vendors)
init_detail = ""
categories_list = ["മേൽ ശാнти ദക്ഷിണ", "മുട്ട് ശാന്തി ദക്ഷിണ", "കഴകക്കാർക്ക് ശമ്പളം", "ശുചിത്വ പ്രവർത്തനങ്ങൾ (Cleaning)", "മെയിൻ്റനൻസ് ജോലികൾ (Maintenance)", "പൂജാ സാധനങ്ങൾ മേടിക്കുന്നത് (Item-wise)", "ഉത്സവകാല ചിലവുകൾ / ഭക്ഷണ വിതരണം"]
init_category_idx = 0
if selected_vendor != "-- പുതിയ ചിലവ് / പുതിയ കട (New Expense) --":
matched_exp = exp_history_df[exp_history_df["item_detail"] == selected_vendor].iloc
init_detail = matched_exp["item_detail"]
if matched_exp["expense_category"] in categories_list:
init_category_idx = categories_list.index(matched_exp["expense_category"])
exp_category = st.selectbox("ചിലവ് ഇനം:", categories_list, index=init_category_idx)
with st.form("expense_form", clear_on_submit=True):
date = st.date_input("തീയതി")
item_detail = st.text_input("വിശദാംശങ്ങൾ / കടയുടെ പേര് *", value=init_detail)
amount = st.number_input("ചിലവായ തുക (₹) *", min_value=1.0, step=10.0)
exp_mode = st.selectbox("പണം നൽകിയ രീതി", ["Cash", "UPI / Bank"])
remarks = st.text_area("മറ്റു വിവരങ്ങൾ")
submit_btn = st.form_submit_button("ചിലവ് സേവ് ചെയ്യുക")
if submit_btn:
if item_detail and amount > 0:
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("INSERT INTO expenses (date, expense_category, item_detail, amount, payment_mode, remarks) VALUES (?,?,?,?,?,?)", (str(date), exp_category, item_detail, amount, exp_mode, remarks))
conn.commit()
conn.close()
st.success("ചിലവ് രേഖപ്പെടുത്തി!")
st.rerun()
elif choice == "📜 റിപ്പോർട്ടുകൾ":
st.subheader("വരവ് ചിലവ് കണക്കു പുസ്തകം")
conn = get_db_connection()
pending_list = pd.read_sql_query("SELECT id, devotee_name, amount, booking_date FROM income WHERE payment_status = 'പിന്നീട് തരും (Pending)'", conn)
if not pending_list.empty:
st.markdown("#### 🔄 പെൻഡിങ് പേയ്‌മെന്റുകൾ മാറ്റാൻ")
pending_options = {f"ID {row['id']}: {row['devotee_name']} - ₹{row['amount']}": row['id'] for _, row in pending_list.iterrows()}
selected_pending = st.selectbox("കാശ് ലഭിച്ച വ്യക്തിയെ തിരഞ്ഞെടുക്കുക:", list(pending_options.keys()))
settle_mode = st.selectbox("പണം ലഭിച്ച മാർഗ്ഗം", ["Cash", "UPI / Bank"])
if st.button("Mark as Paid"):
cursor = conn.cursor()
cursor.execute("UPDATE income SET payment_status = 'പണം ലഭിച്ചു (Paid)', payment_mode = ? WHERE id = ?", (settle_mode, pending_options[selected_pending]))
conn.commit()
st.success("കണക്ക് അപ്ഡേറ്റ് ചെയ്തു!")
st.rerun()
st.markdown("---")
st.markdown("### 📥 വരവുകളുടെ ലിസ്റ്റ് (Income & Bookings)")
# Item-wise Filtering feature added
v_master = pd.read_sql_query("SELECT name FROM vazhipadu_master", conn)["name"].tolist()
filter_options = ["എല്ലാം (Show All)"] + v_master + ["സംഭാവന", "ഭണ്ടാരം വരവ്"]
selected_filter = st.selectbox("🔍 വഴിപാട് ഇനം തിരിച്ച് റിപ്പോർട്ട് കാണാൻ ഫിൽട്ടർ ചെയ്യുക:", filter_options)
if selected_filter == "എല്ലാം (Show All)":
inc_df = pd.read_sql_query("SELECT record_date as 'രേഖപ്പെടുത്തിയ തീയതി', record_time as 'സമയം', booking_date as 'വഴിപാട് തീയതി', income_type as 'ഇനം', vazhipadu_items as 'വഴിപാട് പേര്', devotee_name as 'പേര്', star as 'നക്ഷത്രം', amount as 'തുക (₹)', payment_mode as 'പണം വന്ന രീതി', payment_status as 'അവസ്ഥ' FROM income ORDER BY id DESC", conn)
else:
# Search via SQL LIKE query to filter comma separated values accurately
inc_df = pd.read_sql_query(f"SELECT record_date as 'രേഖപ്പെടുത്തിയ തീയതി', record_time as 'സമയം', booking_date as 'വഴിപാട് തീയതി', income_type as 'ഇനം', vazhipadu_items as 'വഴിപാട് പേര്', devotee_name as 'പേര്', star as 'നക്ഷത്രം', amount as 'തുക (₹)', payment_mode as 'പണം വന്ന രീതി', payment_status as 'അവസ്ഥ' FROM income WHERE vazhipadu_items LIKE '%{selected_filter}%' ORDER BY id DESC", conn)
st.dataframe(inc_df, use_container_width=True)
# Quick sum reminder for filtered item
filtered_total = inc_df['തുക (₹)'].sum()
st.info(f"📊 തിരഞ്ഞെടുത്ത ഇനത്തിന്റെ ആകെ വരവ് തുക: ₹{filtered_total:,.2f}")
st.markdown("### 📤 ചിലവുകളുടെ ലിസ്റ്റ് (Expenses Ledger)")
exp_df = pd.read_sql_query("SELECT date as 'തീയതി', expense_category as 'ചിലവ് ഇനം', item_detail as 'വിശദാംശങ്ങൾ/സാധനം', amount as 'തുക (₹)', payment_mode as 'നൽകിയ രീതി' FROM expenses ORDER BY id DESC", conn)
st.dataframe(exp_df, use_container_width=True)
conn.close()


