from util.log_util import log_info, log_error
import requests

def getPackageIdsAndSalesorderIdFromList(packages, salesorder_number):
    salesorder_ids = []
    package_ids = []
    for package in packages:
        if package['salesorder_number'] == salesorder_number:
            package_ids.append(package['package_id'])

            if package['salesorder_id'] not in salesorder_ids:
                salesorder_ids.append(package['salesorder_id'])

    salesorder_id = ','.join(salesorder_ids)
    package_ids = ','.join(package_ids)
    return salesorder_id, package_ids

def loadAllPackagesShipped(organization_id, authtoken):
    URL = "https://inventory.zoho.com/api/v1/packages?organization_id=" + str(organization_id) + "&authtoken=" + str(authtoken)  # api-endpoint
    log_info("Loading all packages that have not been shipped.")

    all_packages = []

    page = 1
    has_more_page = True

    while(has_more_page):
        api_call = URL + "&filter_by=Status.Shipped&per_page=200&page=" + str(page)
        r = requests.get(api_call)

        data = r.json()
        if data["code"] == 0:
            log_info("Response received for package page " + str(page) + ": " + str(data["message"]))

            loaded_packages = data["packages"]
            all_packages = all_packages + loaded_packages

            if data["page_context"]["has_more_page"] == True:
                has_more_page = True
                page = page + 1
            else:
                has_more_page = False
        else:
            log_error("Error in requesting packages: " + str(data["message"]))
            break
    log_info("Loading in total " + str(len(all_packages)) + " packages that have been shipped.")
    return all_packages


def loadAllPackagesNotShipped(organization_id, authtoken):
    URL = "https://inventory.zoho.com/api/v1/packages?organization_id=" + str(organization_id) + "&authtoken=" + str(authtoken)  # api-endpoint
    log_info("Loading all packages that have not been shipped.")

    all_packages = []

    page = 1
    has_more_page = True

    while(has_more_page):
        api_call = URL + "&filter_by=Status.NotShipped&per_page=200&page=" + str(page)
        r = requests.get(api_call)

        data = r.json()
        if data["code"] == 0:
            log_info("Response received for package page " + str(page) + ": " + str(data["message"]))

            loaded_packages = data["packages"]
            all_packages = all_packages + loaded_packages

            if data["page_context"]["has_more_page"] == True:
                has_more_page = True
                page = page + 1
            else:
                has_more_page = False
        else:
            log_error("Error in requesting packages: " + str(data["message"]))
            break
    log_info("Loading in total " + str(len(all_packages)) + " packages.")
    return all_packages



