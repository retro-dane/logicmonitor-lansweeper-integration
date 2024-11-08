#!/bin/env python
#title           :read_email.py
#description     :Script to read emails sent from Asset Manager Tool with updated assests.
#URL             :None
#author          :Khadane Hood
#notes           :None
#license         :None
#==============================================================================

import secret
import msal 
import json 
import requests
import markets
from datetime import date,timedelta
from addDevices import addDevices,printReport

def get_access_token():
    """
    Generate an access token for Microsoft Graph API.

    Returns:
        str: Access token string.
    """


    # Get tenant ID, client ID, and client secret from secret module
    tenantId = secret.tenantID
    authority = 'https://login.microsoftonline.com/' + tenantId
    clientid = secret.appID
    clientSecret = secret.secretValue
    scope = ['https://graph.microsoft.com/.default']

    # Create a ConfidentialClientApplication object
    app = msal.ConfidentialClientApplication(clientid, authority=authority, client_credential=clientSecret, verify=False)

    # Acquire access token for the client
    access_token = app.acquire_token_for_client(scopes=scope)

    return access_token

def get_email_folder(folderName, token, mailUser):
    """
    Retrieve the ID of the specified email folder for a given user.

    Parameters:
        folderName (str): Name of the email folder to retrieve.
        token (str): Access token for Microsoft Graph API.
        mailUser (str): User's email address or ID.

    Returns:
        str: ID of the specified email folder.
    """
    # Construct the URL for accessing mail folders
    url = f"https://graph.microsoft.com/v1.0/users/{mailUser}/mailFolders/"

    # Set request headers with authorization token and content type
    headers = {"Authorization": f"Bearer {token}", "ContentType": "application/json"}

    # Make a GET request to retrieve mail folders
    response = requests.get(url=url, headers=headers, verify=False)
    data = json.loads(response.text)

    # Iterate through mail folders to find the specified folder by name
    for folder in data["value"]:
        folder_name = folder["displayName"]
        if folderName == folder_name:
            folder_id = folder["id"]
            break

    return folder_id

def send_email_report(content, token, mailUser):
    """
    Send an email with a generated HTML summary report of added devices.

    Parameters:
        content (str): HTML content of the email body (summary report).
        token (str): Access token for Microsoft Graph API.
        mailUser (str): User's email address or ID.

    Returns:
        None
    """

    # Construct the URL for sending emails
    url = f"https://graph.microsoft.com/v1.0/users/{mailUser}/sendMail"

    # Set request headers with content type and authorization token
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}"
    }

    # Construct the payload for the email message
    payload = {
        "message": {
            "subject": "New Device Report",
            "body": {
                "contentType": "text",
                "content": "{}".format(content)
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": "<recipient.email@address.com>"  # Replace with recipient's email address
                    }
                }
            ],
        },
        "saveToSentItems": "true"
    }

    # Convert payload to JSON format
    body = json.dumps(payload)

    # Send POST request to send the email
    response = requests.post(url=url, headers=headers, data=body, verify=False)

    # Check if email was sent successfully
    if response.status_code == 202:
        print("Email Sent")
    else:
        print('Response Body:', response.content)


def main():
    """
    Main function to process email messages and attachments related to assets.

    This function retrieves email messages from a specific mail folder, downloads attachments,
    and processes them to extract asset data. It then generates a summary report
    for the added devices and sends it via email.

    Returns:
        None
    """

    # Get current date and calculate the maximum past date allowed for filtering emails
    currentdate = date.today()
    max_past_date = str(currentdate - timedelta(days=9))

    # Obtain access token for Microsoft Graph API
    access_token = get_access_token()
    token = access_token['access_token']
    token_expiry = access_token["expires_in"]
    mail_user = 'email of mailbox that we are parsing'
    headers = {"Authorization": f"Bearer {token}", "ContentType": "application/json"}

    # Iterate through markets
    for market in markets.markets:

        # Get the mail folder ID for market-specific assets
        mail_folder_id = get_email_folder(folderName=f"{market}Assets", token=token, mailUser=mail_user)

        # Construct API call URL to retrieve emails received since the maximum past date
        url = f"https://graph.microsoft.com/v1.0/users/{mail_user}/mailFolders/{mail_folder_id}/messages?$filter=ReceivedDateTime ge {max_past_date}"

        # Send the API request to retrieve emails
        response = requests.get(url=url, headers=headers, verify=False)
        data = json.loads(response.text)
   
        # Function to retrieve attachments for a specific email message ID
        def get_attachment(message_id):
            url = f"https://graph.microsoft.com/v1.0/users/{mail_user}/mailFolders/{mail_folder_id}/messages/{message_id}/attachments"
            response = requests.get(url=url, headers=headers, verify=False)
            return response.json()

        # Loop through emails in the market assets folder and download the latest attachments
        for mail in data["value"]:
            msgID = mail["id"]
            attachments = get_attachment(msgID)
            for attachment in attachments["value"]:
                attachment_id = attachment["id"]
                attachment_name = attachment["name"]
                download_attachment_endpoint = f"https://graph.microsoft.com/v1.0/users/{mail_user}/mailFolders/{mail_folder_id}/messages/{msgID}/attachments/{attachment_id}/$value"
                header1 = {"Authorization": f"Bearer {token}", "ContentType": "application/octet-stream"}
                response = requests.get(download_attachment_endpoint, headers=header1)

                # Store attachments locally if they are CSV files
                if ".csv" in attachment_name:
                    with open(f"./Downloads/{market}-{attachment_name}", 'wb') as f:
                        f.write(response.content)
                    report = addDevices(f"./Downloads/{market}-{attachment_name}")

        # Generate summary report for added devices
        content = printReport(report)

        # Send email report
        send_email_report(content=content, token=token, mailUser=mail_user)

    # Print token expiry information
    print(f"Token Will Expire in {token_expiry} Days")


if __name__ == '__main__':
    main()