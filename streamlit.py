import gspread
import pandas as pd
from google.oauth2 import service_account
import streamlit as st
import time
from datetime import datetime, timedelta
from gspread_dataframe import get_as_dataframe
from streamlit_js_eval import streamlit_js_eval
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io


google_cloud_secrets = st.secrets["google_cloud"]

creds = service_account.Credentials.from_service_account_info(
    {
        "type": google_cloud_secrets["type"],
        "project_id": google_cloud_secrets["project_id"],
        "private_key_id": google_cloud_secrets["private_key_id"],
        "private_key": google_cloud_secrets["private_key"].replace("\\n", "\n"),
        "client_email": google_cloud_secrets["client_email"],
        "client_id": google_cloud_secrets["client_id"],
        "auth_uri": google_cloud_secrets["auth_uri"],
        "token_uri": google_cloud_secrets["token_uri"],
        "auth_provider_x509_cert_url": google_cloud_secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": google_cloud_secrets["client_x509_cert_url"],
        "universe_domain": google_cloud_secrets["universe_domain"],
    },
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
)



if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()

elapsed_time = datetime.now() - st.session_state.start_time
resetnow = False
if elapsed_time >= timedelta(hours=24):
    resetnow = True



# Connect Google SheetAPI

client = gspread.authorize(creds)
spreadsheet_id = "1plDWCw7-GpkF6LXzAAQfICcvGMpzYzNPn4KeYeQmUus"
# # Authorize and open the Google Sheets by Spreadsheet ID
# client = gspread.authorize(creds)
# spreadsheet_id = "1plDWCw7-GpkF6LXzAAQfICcvGMpzYzNPn4KeYeQmUus"
sheet1 = client.open_by_key(spreadsheet_id).worksheet("Input")
sheet_sub_item = client.open_by_key(spreadsheet_id).worksheet("SubItem")
sheet_vendor = client.open_by_key(spreadsheet_id).worksheet("Vendor")


# Save Sub Item
if 'subitem' not in st.session_state:
    with st.spinner("Ambil Data Sub Item dulu..."):
        st.session_state.subitem = get_as_dataframe(client.open_by_key(spreadsheet_id).worksheet("SubItem"))


# Save Vendor
if 'vendor' not in st.session_state:
    with st.spinner("Ambil Data Vendor dulu..."):
        st.session_state.vendor = get_as_dataframe(client.open_by_key(spreadsheet_id).worksheet("Vendor"))



# Load Data
with st.spinner("Loading data..."):
    sub_item_df = st.session_state.subitem
    vendor_df = st.session_state.vendor


# Upload Image to Google Drive
drive_service = build('drive', 'v3', credentials=creds)

def upload_image_to_drive(image_bytes, image_name):
    # ID folder tujuan
    folder_id = '1aWrJRzib2ZY0enJxybNcsv828qQ2L-DY'

    # Upload the image to Google Drive
    media = MediaIoBaseUpload(io.BytesIO(image_bytes), mimetype='image/jpeg')
    file_metadata = {
        'name': image_name,
        'parents': [folder_id]  # Tentukan folder tempat file akan disimpan
    }
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # Make the file publicly accessible by updating the sharing permissions
    drive_service.permissions().create(fileId=file['id'], body={'role': 'reader', 'type': 'anyone'}).execute()

    # Generate the shareable URL
    file_url = f"https://drive.google.com/uc?id={file['id']}"
    return file_url




st.title("Form Input Data")

date = st.date_input("Date", value=datetime.today(), disabled=True)

no_nota = st.text_input("Masukkan angka (maksimal 4 digit):", max_chars=4)


lastwednesday = date - pd.tseries.offsets.Week(weekday=2)
# If today wednesday = today else lastwednesday
if date.weekday() == 2:
    lastwednesday = date
deliverydate = st.date_input("Delivery Date", value=lastwednesday)
# DeliveryDate should Wednesday

if deliverydate.weekday() != 2:
    st.error("Delivery Date should be Wednesday")
    st.stop()

checksup = st.checkbox("New Supplier")
if checksup:
    supplier = st.text_input("Supplier", key='supplier')
    if supplier not in vendor_df['Vendor'].values and supplier != "":
        st.warning("Supplier belum ada. Apakah ingin menambahkan?")
        confirm = st.button("Confirm", key='confirm')
        if confirm: 
            sheet_vendor.append_row([supplier])
    if supplier in vendor_df['Vendor'].values:
        st.warning("Supplier Sudah ada! Apakah ingin mengubah Supplier?")
else:
    supplier = st.selectbox("Supplier", options=["Pilih Vendor"] + list(vendor_df['Vendor']), key='supplier')

# kategori deafault "Pilih Kategori"
kategori = st.selectbox("Kategori", options=["Pilih Kategori"] + sorted(sub_item_df["kategori"].astype(str).unique()), index=0, key="kategori")
checksub = st.checkbox("New Sub item", key='sub')
if checksub:
    sub = st.text_input("Sub Item")
    if sub not in sub_item_df['subitem'].values and sub != "":
        st.warning("Sub Item belum ada. Apakah ingin menambahkan?")
        confirm = st.button("Confirm", key='confirm')
        if confirm:
            sheet_sub_item.append_row([kategori, sub])
    if sub in sub_item_df['subitem'].values:
        st.warning("Sub Item Sudah ada! Apakah ingin mengubah Sub Item?")
else:
    if kategori:
        dropsubitem = sorted(sub_item_df[sub_item_df["kategori"] == kategori]["subitem"].astype(str).unique())

    sub = st.selectbox("Sub", sorted(dropsubitem))


nilai = st.number_input("Nilai", key='nilai')
cbm = st.number_input("CBM", key='cbm')
image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key='image')



submit_button = st.button("Submit", key='submit')

# Input box


if submit_button:
    if image: 
        image_bytes = image.getvalue()
        image_url = upload_image_to_drive(image_bytes, image.name)
    else:
        image_url = "No image uploaded"
    
    date_str = date.strftime("%d/%m/%Y")
    delivery_date = deliverydate.strftime("%d/%m/%Y")
    
    # Append data to Google Sheets
    sheet1.append_row([date_str,no_nota, delivery_date,supplier, kategori, sub, nilai ,cbm , image_url])
    
    # Display success message
    st.success("Data berhasil disimpan ke Google Sheets!")
    
    # Refresh the page after submitting the data
    time.sleep(1)
    if resetnow == True:
        st.session_state.clear()
    streamlit_js_eval(js_expressions="parent.window.location.reload()")
