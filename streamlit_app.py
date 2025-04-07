import streamlit as st
from PIL import Image
import pytesseract
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import io
import pandas as pd

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# Streamlit UI
st.title("📸 Workout Screenshot to Google Sheet")

uploaded_file = st.file_uploader("Upload a screenshot of your workout plan", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded workout screenshot", use_column_width=True)

    # OCR Processing
    with st.spinner("Extracting workout text..."):
        text = pytesseract.image_to_string(image)

    st.subheader("📄 Extracted Text")
    st.text(text)

    # Try parsing simple table format (can improve later!)
    lines = text.strip().split("\n")
    parsed_data = [line.split() for line in lines if line.strip()]
    df = pd.DataFrame(parsed_data)

    st.subheader("📋 Parsed Workout Table (Editable Soon)")
    st.dataframe(df)

    sheet_name = st.text_input("Google Sheet name (we'll create it if needed)", "MyWorkoutLog")

    if st.button("Send to Google Sheet"):
        try:
            sheet = client.open(sheet_name).sheet1
        except gspread.SpreadsheetNotFound:
            sheet = client.create(sheet_name).sheet1

        sheet.clear()
        sheet.update([df.columns.tolist()] + df.values.tolist())
        st.success("✅ Data sent to Google Sheet!")
