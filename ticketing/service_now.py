# ticketing_system.py
import requests
from requests.auth import HTTPBasicAuth
import logging

# Define logger
logger = logging.getLogger(__name__)

# Function to log ticket in ServiceNow
def log_ticket_in_service_now(extracted_info: dict):
    try:
        # ServiceNow credentials and instance details
        servicenow_url = "https://yourinstancename.service-now.com/api/now/table/incident"
        servicenow_user = "username"
        servicenow_password = "password"
        
        # Headers for the API request
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Payload for creating an incident ticket
        payload = {
            "short_description": extracted_info.get("issue_description", "No issue description provided"),
            "description": f"Reported by: {extracted_info.get('name', 'Unknown')}, Issue: {extracted_info.get('issue_description', 'No issue description provided')}",
            "priority": map_priority_to_servicenow(extracted_info.get("priority", "low")),
            "caller_id": extracted_info.get("name", "Unknown")
        }
        
        # Send POST request to create a ticket
        response = requests.post(
            servicenow_url,
            auth=HTTPBasicAuth(servicenow_user, servicenow_password),
            headers=headers,
            json=payload
        )

        # Parse the response from ServiceNow
        if response.status_code == 201:
            result = response.json().get("result", {})
            ticket_number = result.get("number", "Unknown")
            logger.info(f"Ticket logged successfully with Ticket Number: {ticket_number}")
            return ticket_number
        else:
            logger.error(f"Failed to log ticket. Status Code: {response.status_code}, Response: {response.text}")
            return None

    except Exception as e:
        logger.error(f"Error logging ticket in ServiceNow: {str(e)}")
        return None

# Helper function to map priority to ServiceNow's priority levels
def map_priority_to_servicenow(priority: str) -> str:
    priority_map = {
        "high": "1",
        "medium": "2",
        "low": "3"
    }
    return priority_map.get(priority.lower(), "4")
