# Lansweeper to LogicMonitor Integration

## Overview

This integration automates the process of transferring asset reports from Lansweeper to LogicMonitor for centralized monitoring and management. Lansweeper generates asset reports and sends them to a central email address. The provided scripts parse these reports and upload the data to LogicMonitor, enabling efficient asset monitoring and management.

## Prerequisites

- Lansweeper account with report generation capability
- LogicMonitor account with API access
- Python 3.x installed
- Required Python libraries: requests, json, csv
- Access to Microsoft Graph API for email retrieval (if applicable)

## Setup Instructions

1. **Configure Lansweeper Reports**: Set up Lansweeper to generate asset reports and send them to a designated central email address.

2. **Generate LogicMonitor API Credentials**: Obtain API credentials from LogicMonitor to authenticate API requests.

3. **Install Dependencies**: Install required Python libraries using pip: pip -r requirements.txt

5. **Configure Script Parameters**: Update the necessary parameters in the script files ( `secret.py`,`market.py`, `main.py`) with your Lansweeper, LogicMonitor, and email settings.

6. **Run the Scripts**: Execute the main script to initiate the integration process:


## Functionality

- **Email Retrieval**: The script retrieves asset reports from the designated email folder using the Microsoft Graph API.
- **Data Parsing**: It parses the received CSV reports to extract relevant asset information.
- **LogicMonitor Upload**: The extracted data is uploaded to LogicMonitor using the LogicMonitor API for centralized monitoring.



