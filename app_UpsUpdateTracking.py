import requests
import logging
import argparse
import packagetracker

from util.log_util import log_info, log_error, log_warn
from util.db_util import loadAllPackagesShipped

def mark_as_delivered(shipmentorder_id, organization_id, authtoken, package_number):
    api_call = "https://inventory.zoho.com/api/v1/shipmentorders/"+ str(shipmentorder_id)+"/status/delivered?organization_id="+str(organization_id) + "&authtoken=" + str(authtoken)
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}
    log_info("Marking Package Number " + str(package_number) + " as delivered using apicall " + str(api_call))

    r = requests.post(api_call, headers=headers)
    data = r.json()
    if data["code"] == 0:
        log_info("Response received for [package_number=" + str(package_number) + "]: " + str(data["message"]))
    else:
        log_error("[package_number=" + str(package_number) + "]: " + str(data["message"]))

if __name__ == '__main__':
    """
        Reads all current shipments from Zoho Inventory, checks the tracking status and updates Zoho Inventory accordingly
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--authtoken', help='Zoho auth token', required=True)
    parser.add_argument('-o', '--organization_id', help='Organization ID', required=True)
    parser.add_argument('-log', '--log_file', help='File destination of application log', required=True)

    args = parser.parse_args()

    organization_id = args.organization_id
    authtoken = args.authtoken
    log_file = args.log_file

    logging.basicConfig(filename=log_file, level=logging.INFO)
    log_info("------- APPLICATION STARTED --------")
    log_info("Organization ID is set to: " + str(organization_id))
    log_info("Authtoken is: " + str(authtoken))

    tracker = packagetracker.PackageTracker()

    #1st read all current shipments that are not completed yet
    shipments_to_track = loadAllPackagesShipped(organization_id=organization_id, authtoken=authtoken)

    #2 take tracking numbers and track status
    for shipment in shipments_to_track:
        tracking_id = shipment['tracking_number']

        if len(str(tracking_id)) > 0:
            try:
                package = tracker.package(str(tracking_id))
                info = package.track()
                if info.status == "Delivered" or ("Package delivered by local post office" in info.status):
                    log_info("Package has " + str(shipment["package_number"]) + " has been delivered.")
                    mark_as_delivered(shipmentorder_id=shipment["shipment_id"], organization_id=organization_id, authtoken=authtoken, package_number=shipment["package_number"])
            except:
                log_warn("Shipment tracking for package number " + str(shipment["package_number"] + " is invalid. Skipped."))
                continue
        else:
            log_error("Shipment does not have tracking: " + str(shipment["package_number"]))
    log_info("------- APPLICATION ENDED --------")
