import datetime
from google.oauth2 import service_account
import streamlit as st
import gspread
import pandas as pd


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
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
)

client = gspread.authorize(creds)
spreadsheet_id = "1plDWCw7-GpkF6LXzAAQfICcvGMpzYzNPn4KeYeQmUus"

def get_data():
    

    subitem = client.open_by_key(spreadsheet_id).worksheet('SubItem').get_all_records()
    vendor = client.open_by_key(spreadsheet_id).worksheet('Vendor').get_all_records()

    subitem = pd.DataFrame(subitem)
    vendor = pd.DataFrame(vendor)
    return subitem, vendor



def input_supplier(supplier):
    sheet = client.open_by_key(spreadsheet_id).worksheet('Vendor')
    sheet.append_row([supplier])

def input_subitem(subitem, kategori):
    sheet = client.open_by_key(spreadsheet_id).worksheet('SubItem')
    data = [subitem, kategori]
    sheet.append_row(data)



def input_data(date, nota, delivery_date, supplier, kategori, sub, nilai, cbm, image_url):

    sheet = client.open_by_key(spreadsheet_id).worksheet("Input")

    data = [date, nota, delivery_date, supplier, kategori, sub, nilai,cbm, image_url]
    sheet.append_row
    st.write("testing")