import pandas as pd
import requests
import json
import logging
import numpy as np
import argparse

from util.log_util import log_info, log_error,log_warn
from util.db_util import getPackageIdsAndSalesorderIdFromList, loadAllPackagesNotShipped

def load_ups_file(file_name, packages):
    available_salesorder_numbers = []

    for package in packages:
        if package["salesorder_number"] not in available_salesorder_numbers:
            available_salesorder_numbers.append(package["salesorder_number"])

    df_data = pd.read_csv(file_name, ",", header=None)
    df_data.columns = ['voided', 'tracking_number', 'name1', 'name2', 'sales_order']
    log_info(str("Succesfully loaded input file with " + str(len(df_data)) + " entries."))

    voided = df_data[df_data['voided'] == "Y"]
    log_info(str(str(len(voided)) + " rows of the input file are voided, thus ignored."))

    df_data = df_data[df_data['voided'] == "N"]

    null_tracking = df_data[df_data['tracking_number'].isnull()]
    if(len(null_tracking) > 0):
        for index, row in null_tracking.iterrows():
            msg = "Cannot process the following entry: [tracking_number=" + str(row['tracking_number']) + " ; sales_order=" + str(row['sales_order']) + "]"
            log_warn(msg)

    null_sales_order = df_data[df_data['sales_order'].isnull()]
    if(len(null_sales_order) > 0):
        for index, row in null_sales_order.iterrows():
            msg = "Cannot process the following entry: [tracking_number=" + str(row['tracking_number']) + " ; sales_order=" + str(row['sales_order']) + "]"
            log_warn(msg)

    df_data = df_data[df_data['tracking_number'].notnull()]
    df_data = df_data[df_data['sales_order'].notnull()]

    df_data_available = df_data[df_data['sales_order'].isin(available_salesorder_numbers)]

    mask_notin = np.logical_not(df_data['sales_order'].isin(available_salesorder_numbers))
    df_data_notavailable = df_data[mask_notin]

    log_info(str(len(df_data_notavailable)) + " entries are not available in packages list. Stored to UPDATE_NEXT.CSV")
    df_data_notavailable.to_csv("files/UPDATE_NEXT.CSV", index=None, header=None)

    log_info(str("Succesfully prepared input file. Using " + str(len(df_data_available)) + " entries."))
    return df_data_available

def create_shipment(tracking_number, delivery_method="UPS", shipping_charge=None, exchange_rate=None, template_id=None, notes=None):
    """
    Create the parameters for a new shipment order
    For more details, see: https://www.zoho.com/inventory/api/v1/#Shipment_Orders_Create_a_Shipment_Order
    :return: String with JSON content
    """

    param = dict()
    param["reference_number"] = str(tracking_number)
    param["delivery_method"] = str(delivery_method)
    param["tracking_number"] = str(tracking_number)

    if shipping_charge != None:
        param["shipping_charge"] = int(shipping_charge)

    if exchange_rate != None:
        param["exchange_rate"] = int(exchange_rate)

    if template_id != None:
        param["template_id"] = int(template_id)

    if notes != None:
        param["notes"] = str(notes)

    content = "JSONString=" + json.dumps(param) + ""
    return content

if __name__ == '__main__':
    """
        Automate adding tracking numbers to shipment orders from UPS export files
        For more details, see: https://www.zoho.com/inventory/api/v1/#Shipment_Orders_Create_a_Shipment_Order
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_csv', help='Input CSV file of USP tracking numbers', required=True)
    parser.add_argument('-a', '--authtoken', help='Zoho auth token', required=True)
    parser.add_argument('-o', '--organization_id', help='Organization ID', required=True)
    parser.add_argument('-log', '--log_file', help='File destination of application log', required=True)

    args = parser.parse_args()

    organization_id = args.organization_id
    authtoken = args.authtoken
    input_file = args.input_csv
    log_file = args.log_file

    logging.basicConfig(filename=log_file, level=logging.INFO)
    log_info("------- APPLICATION STARTED --------")
    URL = "https://inventory.zoho.com/api/v1/shipmentorders?organization_id=" + str(organization_id) + "&authtoken=" + str(authtoken) # api-endpoint

    #input_file = "files/UPS_CSV_EXPORT_test.csv"

    log_info("Processing file: " + input_file)
    log_info("Organization ID is set to: " + str(organization_id))
    log_info("Authtoken is: " + str(authtoken))
    log_info("API endpoint is set to: " + str(URL))

    all_packages = loadAllPackagesNotShipped(organization_id=organization_id, authtoken=authtoken)

    ups_data = load_ups_file(input_file, packages=all_packages)
    
    for index, row in ups_data.iterrows():
        log_info("Creating Shipment order for entry: [tracking_number=" + str(row['tracking_number']) + " ; sales_order=" + str(row['sales_order']) + "]")

        salesorder_number = row['sales_order']
        salesorder_id, package_ids = getPackageIdsAndSalesorderIdFromList(all_packages, salesorder_number=salesorder_number)

        payload = create_shipment(tracking_number=row['tracking_number'])
        headers = {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}

        api_call = URL + "&salesorder_id=" + salesorder_id + "&package_ids=" + package_ids

        log_info("Sending POST request with payload [" + payload + "] to " + api_call)
        r = requests.post(api_call, data=payload, headers=headers)

        data = r.json()
        if data["code"] == 0:
            log_info("Response received for [tracking_number=" + str(row['tracking_number']) + " ; sales_order=" + str(
                row['sales_order']) + "]: " + str(data["message"]))
        else:
            log_error("[tracking_number=" + str(row['tracking_number']) + " ; sales_order=" + str(
                row['sales_order']) + "]: " + str(data["message"]))

    log_info("------- APPLICATION ENDED --------")
