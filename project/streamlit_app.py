import streamlit as st
from app import process_lead, log_lead
import pandas as pd
import os

st.set_page_config(page_title="Website Conversion System", page_icon=":clipboard:")

st.title("Website Conversion System")
st.write("Submit a service request and see how the system processes it.")
st.caption("This demo simulates the front-office to back-office workflow for a home services company.")
st.caption(" It captures leads, qualifies them, routes next steps, logs results, and shows lightweight reporting.")
st.caption("BONUS: Try out English and Spanish messages, incomplete inputs, or suspicious/spam text to see the language detection in action!")

with st.form("lead_form"):
    name = st.text_input("Name")
    phone = st.text_input("Phone Number")
    message = st.text_area("Service Request/Message")
    timeline_options = {
        "ASAP": "asap",
        "Today": "today",
        "This week": "this week",
        "Soon": "soon",
        "Just browsing": "just browsing"
    }
    timeline_label = st.selectbox("Timeline for Service", list(timeline_options.keys()))
    timeline = timeline_options[timeline_label]
    submit_button = st.form_submit_button("Submit")

if submit_button:
    result = process_lead(name, phone, message, timeline)
    log_lead(result)

    st.subheader("Lead Processing Result")
    st.json(result)

    st.subheader("Operational Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Service Category", result["service_category"])
    col2.metric("Urgency", result["urgency"])
    col3.metric("Lead Result", result["qualification_result"])

    col4, col5, col6 = st.columns(3)
    col4.metric("Classification Method", result["classification_method"])
    col5.metric("Booking Outcome", result["booking_outcome"])
    col6.metric("Follow-Up Action", result["follow_up_action"])

    st.markdown(f"**Operational Details**")
    st.write(f"Service Category: {result['service_category']}")
    st.write(f"Urgency: {result['urgency']}")
    st.write(f"Lead Result: {result['qualification_result']}")
    st.write(f"Classification Method: {result['classification_method']}")
    st.write(f"Booking Outcome: {result['booking_outcome']}")
    st.write(f"Follow-Up Action: {result['follow_up_action']}")

    if result["qualification_result"] == "Qualified":
        st.success("Lead is qualified and has been routed to the next step.")
    elif result["qualification_result"] == "Incomplete":
        st.warning(f"Lead is incomplete: {result['error_reason']}")
    elif result["qualification_result"] == "Suspicious":
        st.error(f"Lead is flagged as suspicious: {result['error_reason']}")
    elif result["qualification_result"] == "Needs Review":
        st.info(f"Lead needs manual review: {result['error_reason']}")
    else:
        st.info("Lead requires manual review or follow-up based on the processing results.")

    if result["company_notified"]:
        st.subheader("Internal Alert")
        if result["qualification_result"] == "Suspicious":
            st.error("Company has been notified of potential spam for immediate attention.")
        elif result["urgency"] == "High":
            st.info("Company has been notified of a high urgency lead for immediate attention.")
        else: 
            st.info("Company has been notified based on lead processing results and workflow rules.")

if os.path.exists("lead_log.csv"):
    st.subheader("Lead Log")
    df_lead_log = pd.read_csv("lead_log.csv")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Leads", len(df_lead_log))
    m2.metric("Qualified Leads", (df_lead_log["qualification_result"] == 'Qualified').sum())
    m3.metric("Suspicious Leads", (df_lead_log["qualification_result"] == 'Suspicious').sum())
    m4.metric("Spanish", (df_lead_log["language"] == "Spanish").sum())
    m5.metric("High Urgency", (df_lead_log["urgency"] == "High").sum())

    display_cols = [
        "timestamp",
        "name",
        "service_category",
        "urgency",
        "qualification_result",
        "routing_decision",
        "booking_outcome",
        "follow_up_action",
        "crm_status",
        "lead_stage",
        "classification_method"
    ]

    st.dataframe(df_lead_log[display_cols].tail(10).iloc[::-1], use_container_width=True)