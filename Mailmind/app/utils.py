import re
import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup   
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import time



def extract_details(text):

    text = re.sub(r'\b(from|to)\b', '', text, flags=re.IGNORECASE).strip()

    
    pincode_pattern = r'\b\d{6}\b'  
    pincode_match = re.search(pincode_pattern, text)
    pincode = pincode_match.group() if pincode_match else None

    if pincode:
        text = text.replace(pincode, "").strip()


    contact_pattern = r'\b\d{10}\b'  
    contact_match = re.search(contact_pattern, text)
    contact = contact_match.group() if contact_match else None

    
    if contact:
        contact = f"+91{contact}"
        text = text.replace(contact[3:], "").strip()  

   
    parts = text.split(',', 1)
    name = parts[0].strip() if parts else None
    address = parts[1].strip() if len(parts) > 1 else None

    return {
        "name": name.title() if name else None,  
        "address": address.title() if address else None,  
        "pincode": pincode,
        "contact": contact
    }

def get_address_details(address):
    
    load_dotenv()

    # Retrieve API key
    API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    if not API_KEY:
        raise ValueError("Google Maps API key not found in environment variables.")

    
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            result = data['results'][0]
            address_components = result['address_components']
            geometry = result['geometry']['location']
            
            pincode = next(
                (comp['long_name'] for comp in address_components 
                 if 'postal_code' in comp['types']), 
                None
            )
            
            return {
                'pincode': pincode,
                'latitude': geometry['lat'],
                'longitude': geometry['lng'],
            }
    
    # Raise an exception if API fails or status is not OK
    raise ValueError(f"Failed to fetch address details for: {address}. Response: {response.text}")

def get_pincode_from_scrap(address):
    # Perform a Google search for the address
    query = '+'.join(address.split())  # Convert address to query format
    url = f'https://www.google.com/search?q={query}'

    # Send the request to Google (this might need a user-agent header to work properly)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return "Error: Could not retrieve the page."
    
    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the result with pin code or postal code
    # Pin codes are usually a sequence of 6 digits, but it can vary based on country
    # You can adjust this regex if needed
    pin_code_pattern = r'\b\d{6}\b'
    pin_code_matches = re.findall(pin_code_pattern, soup.get_text())
    
    if pin_code_matches:
        return pin_code_matches[0]  # Return the first match (assuming it is the correct one)
    else:
        return None


# Load environment variables
load_dotenv()
subscription_key = os.getenv('subscription_key')
endpoint = "https://pibit-azure-ocr-paid.cognitiveservices.azure.com/"


computervision_client = ComputerVisionClient(
    endpoint, CognitiveServicesCredentials(subscription_key)
)

def azure_ocr_extract(image_path):
   
    try:
        
        with open(image_path, "rb") as image_stream:
            # Start the read operation with cropping
            read_response = computervision_client.read_in_stream(image_stream, raw=True)

        
        operation_location = read_response.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

        
        while True:
            read_result = computervision_client.get_read_result(operation_id)
            if read_result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
                break
            time.sleep(1)

        
        text = " "
        if read_result.status == OperationStatusCodes.succeeded:
            for page in read_result.analyze_result.read_results:
                for line in page.lines:
                    text = text + line.text + " "
                return text
        
    except Exception as e:
        print(f"Error reading text: {str(e)}")
        return ""
    
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")


# from twilio.rest import Client

# def send_whatsapp_message(to, message):
#     """
#     Send a WhatsApp message using Twilio API.
#     Args:
#         to (str): Recipient's WhatsApp number (e.g., "whatsapp:+91XXXXXXXXXX").
#         message (str): Message to be sent.
#     """
#     try:
#         client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#         message = client.messages.create(
#             body=message,
#             from_=TWILIO_WHATSAPP_NUMBER,
#             to=to
#         )
#         print(f"Message sent with SID: {message.sid}")
#     except Exception as e:
#         print(f"Failed to send message: {str(e)}")
from twilio.rest import Client

def send_whatsapp_notification(sender_name,sender_contact, receiver_address, provided_pincode, modified_pincode):
    """
    Sends a WhatsApp notification to the sender to confirm the address pincode.
    """
    client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))

    message_body = (
        f"Hello!{sender_name} The receiver address you provided is:\n\n"
        f"{receiver_address}\n\n"
        f"The pincode you provided is: {provided_pincode}\n"
        f"The correct pincode for this address is: {modified_pincode}\n\n"
        f"Do you want to update the pincode to the correct one? Reply with 'Yes' to confirm or 'No' for manual correction."
    )

    try:
        message = client.messages.create(
            from_=os.getenv('TWILIO_WHATSAPP_NUMBER'),
            to=f"whatsapp:{sender_contact}",
            body=message_body
        )
        print(f"Message sent with SID: {message.sid}")
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")


