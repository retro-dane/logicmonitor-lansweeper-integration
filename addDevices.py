#!/bin/env python
#title           :addDevices.py
#description     :Script to facilitate updating Monitoring Tool inventory with devices from Asset Management. Script will pick up a CSV file on a scheduled basis, parse the info and add new assets if found to Monitoring Tool.
#URL             :None
#author          :Khadane Hood
#notes           :None
#license         :None
#==============================================================================
 
import requests
import json
import hashlib
import base64
import time
import hmac
import csv
import secret
from prettytable import PrettyTable
from prettytable.colortable import ColorTable, Themes


def addDevices(pathToFile):
    """
    Add devices to the LogicMonitor platform using information from a CSV file.

    Parameters:
        pathToFile (str): The path to the CSV file containing device information.

    Returns:
        list: A list of device display names that were successfully added to LogicMonitor.
    """
    import csv
    import json
    import requests
    import time
    import hmac
    import hashlib
    import base64

    deviceCount = 0  # Initialize the device count
    deviceList = []  # Initialize the list to store device names
    
    # Proxies configuration (if needed)
    proxy = {
        'http': 'http://example.proxy.com'
    }

    # Read data from the CSV file
    with open(pathToFile, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # Iterate through each row in the CSV file
        for row in reader:
            displayname = row["AssetName"]
            ip = row["IPAddress"]
            location = ["Location"]
            description = row["Description"]
            department = row["Department"]
            contact = row["Contact"]

            # Request Info
            httpVerb ='POST'
            resourcePath = '/device/devices'
            queryParams = ''
            data = '{"key": "value", "key1": "value2" }'

            # Construct URL
            url = 'https://'+ secret.Company +'.logicmonitor.com/santaba/rest' + resourcePath +queryParams

            # Get current time in milliseconds
            epoch = str(int(time.time() * 1000))

            # Concatenate Request details
            requestVars = httpVerb + epoch + data + resourcePath

            # Construct signature 
            digest = hmac.new(
                    secret.AccessKey.encode('utf-8'),
                    msg=requestVars.encode('utf-8'),
                    digestmod=hashlib.sha256).hexdigest()
            signature = base64.b64encode(digest.encode('utf-8')).decode('utf-8')  

            # Construct headers
            auth = 'LMv1 ' + secret.AccessId + ':' + str(signature) + ':' + epoch
            headers = {'Content-Type':'application/json','Authorization':auth,'X-Version':'3'}

            # Make request to add device
            response = requests.post(url, data=data, headers=headers, proxies=proxy, verify=False)

            print('URL:', url)
            print('Response Status:', response.status_code)
            
            # If the request is successful (status code 200), increment device count and add display name to the list
            if response.status_code == 200:
                deviceCount += 1
                deviceList.append(displayname)
            
            print('Response Body:', response.content)
    
    return deviceList  # Return the list of device display names


def printReport(device_List): 
    """
    Generate and print a report of recently added devices.

    Parameters:
        device_List (list): A list of recently added devices.

    Returns:
        prettytable.PrettyTable: A PrettyTable object representing the report table.
    """
    # Import PrettyTable library to create a formatted table
    from prettytable import PrettyTable

    # Get the number of devices in the list
    count = len(device_List)    

    # Create a PrettyTable object with title and field names
    myTable = PrettyTable()
    myTable.title = "Recently Added Devices"
    myTable.field_names = [" # ", "Device Name"]
    myTable._max_width = {"#": 50, "Device Name": 100}  
    myTable._min_width = {"#": 50, "Device Name": 60}   

    if count == 0:
        myTable.add_row([" ", "No new devices added today"])
        return myTable
    else:
        # Add each device to the table
        for x in range(1, count):
            myTable.add_row([f"{x}", f"{device_List[x]}"], divider=True)
        
        # Print the table and the total count of new devices
        print(myTable)
        print("New Device Total: %s" % count)
        return myTable
