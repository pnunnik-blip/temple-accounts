import streamlit as st
from datetime import datetime

from sheets import (
    get_vazhipadu_master,
    get_payment_master,
    save_income
)


def show():

    st.header("🙏 വഴിപാട് വരവ് ചേർക്കുക")
    st.markdown("---")


    # -----------------------------
    # Load Master Data
    # -----------------------------

    vazhipadu_response = get_vazhipadu_master()

    if vazhipadu_response.get("status") != "success":
        st.error("Unable to load Vazhipadu Master")
        return


    vazhipadu_list = vazhipadu_response["data"]


    payment_response = get_payment_master()

    if payment_response.get("status") != "success":
        st.error("Unable to load Payment Master")
        return


    payment_list = payment_response["data"]



    # -----------------------------
    # Prepare display data
    # -----------------------------

    active_vazhipadu = {

        item["name"]: item["amount"]

        for item in vazhipadu_list

        if item["active"] == "Yes"

    }


    payment_modes = [

        item["name"]

        for item in payment_list

    ]



    # -----------------------------
    # Income Form
    # -----------------------------

    with st.form("income_form"):


        name = st.text_input(
            "പേര് (Devotee Name)"
        )


        star = st.text_input(
            "നക്ഷത്രം (Star)"
        )


        selected_items = st.multiselect(

            "വഴിപാടുകൾ തിരഞ്ഞെടുക്കുക",

            list(active_vazhipadu.keys())

        )


        total = 0


        items = []


        for item in selected_items:


            amount = active_vazhipadu[item]


            total += amount


            items.append({

                "name":item,

                "amount":amount

            })



        st.info(
            f"ആകെ തുക (Total): ₹ {total}"
        )


        payment_mode = st.selectbox(

            "Payment Mode",

            payment_modes

        )


        remarks = st.text_input(
            "Remarks"
        )



        submit = st.form_submit_button(
            "Save Receipt"
        )



        if submit:


            if not name:

                st.error(
                    "Please enter devotee name"
                )

                return


            if len(items)==0:

                st.error(
                    "Please select Vazhipadu"
                )

                return



            data = {


                "name":name,

                "star":star,

                "total_amount":total,

                "payment_mode":payment_mode,

                "remarks":remarks,

                "items":items

            }



            response = save_income(data)



            if response.get("status")=="success":


                st.success(

                    f"✅ Receipt Saved Successfully\n\nReceipt No: {response['receipt_no']}"

                )


            else:

                st.error(
                    response.get(
                        "message",
                        "Save failed"
                    )
                )