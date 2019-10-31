# ZohoInventory-UPSWorldShip-Integration
Collection of scripts that 1) insert tracking numbers from UPS WorldShip exported CSV into Zoho Inventory and 2) mark shipments as delivered. These scripts leverage the Zoho Inventory v1 API and the UPS API.

Run these scripts on your own risk - no warranty!

# Requirements
These scripts require the installation and setup of the *packagetracker* package which can be found here: https://github.com/alertedsnake/packagetracker

# Usage
## Insert Tracking Numbers from WorldShip CSV File
After creating your labels and tracking numbers using WorldShip, export a CSV file that has the following columns:
1. Voided (Y or N)
2. Tracking Number
3. Address
4. Organization
5. Shipment Number

An example file can be found [here](https://github.com/Julian-Theis/ZohoInventory-UPSWorldShip-Integration/blob/master/files/UPS_WorldShip_Export.csv).

Then run the script with the following parameters:
```
python app_UpsInsertTrackingNumbers.py -i <WorldShip CSV File location> -a <authtoken> -o <organization id> -log <destination of log file>
```

## Check Shipment Tracking and Mark Shipment as Delivered
Run the following command to automatically load all shipments in shipping status, track their status, and mark them as delivered if the packages arrived at their destination.
Then run the script with the following parameters:
```
python app_UpsUpdateTracking.py -a <authtoken> -o <organization id> -log <destination of log file>
```
