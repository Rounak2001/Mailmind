# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework import viewsets
# from .serializers import ScannedPostSerializer
# from .models import PostData
# from .models import PincodeMapping
# from rest_framework.response import Response
# from PIL import Image
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator
# from .utils import (
#     extract_details,
#     get_address_details,
#     get_pincode_from_scrap,
#     azure_ocr_extract
# )


# def check_merged_pincode(pincode):

#     mapping = PincodeMapping.objects.filter(old_pincode=pincode).first()
#     return mapping.new_pincode if mapping else pincode


# def handle_uploaded_file(image, image_path):
    
#     with open(image_path, "wb") as temp_file:
#         for chunk in image.chunks():  # Safely write the file in chunks
#             temp_file.write(chunk)

# @csrf_exempt
# class ProcessPostDataView(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request, *args, **kwargs):
#         # Retrieve the uploaded files
#         image1 = request.FILES.get('senderImage')
#         image2 = request.FILES.get('receiverImage')
#         print(f"Request method: {request.method}")
#         print(f"Request files: {request.FILES}")
#         print(f"Request data: {request.data}")


#         if not image1 or not image2:
#             return Response(
#                 {"error": "Both fields (image1 and image2) are required."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # # Save the images temporarily
#         # image_path1 = f"/tmp/{image1.name}"
#         # handle_uploaded_file(image1, image_path1)
#         # image_path2 = f"/tmp/{image2.name}"
#         # handle_uploaded_file(image2, image_path2)
#         import os
#         from django.conf import settings

#         image_path1 = os.path.join(settings.MEDIA_ROOT, 'post_images', image1.name)
#         image_path2 = os.path.join(settings.MEDIA_ROOT, 'post_images', image2.name)

# # Ensure the directory exists
#         os.makedirs(os.path.dirname(image_path1), exist_ok=True)
#         # Verify the images
#         try:
#             for image_path in [image_path1, image_path2]:
#                 img = Image.open(image_path)
#                 img.verify()
#                 print(f"Valid image: {image_path}")
#         except Exception as e:
#             return Response(
#                 {"error": f"Invalid image file: {str(e)}"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Process images and extract text
#         try:
#             sender_text = azure_ocr_extract(image_path1)
#             receiver_text = azure_ocr_extract(image_path2)

#             # Extract details
#             sender_details = extract_details(sender_text)
#             receiver_details = extract_details(receiver_text)

#             sender_name = sender_details.get("name")
#             sender_address = sender_details.get("address")
#             sender_pincode = sender_details.get("pincode")
#             sender_contact = sender_details.get("contact")

#             receiver_name = receiver_details.get("name")
#             receiver_address = receiver_details.get("address")
#             receiver_pincode = receiver_details.get("pincode")
#             receiver_contact = receiver_details.get("contact")

#             # Get geocoded address details
#             fetched_address = get_address_details(receiver_address)
#             fetched_pincode = fetched_address.get("pincode")
#             latitude = fetched_address.get("latitude")
#             longitude = fetched_address.get("longitude")

#             # Fallback to scraping if geocoding fails
#             if fetched_pincode is None:
#                 fetched_pincode = get_pincode_from_scrap(receiver_address)

#             # Handle modified pincode logic
#             modified_pincode = None
#             if fetched_pincode and fetched_pincode != receiver_pincode:
#                 modified_pincode = fetched_pincode

#             # Save post data
#             post_data = PostData.objects.create(
#                 image1 = image1,
#                 image2 = image2,
#                 sender_name=sender_name,
#                 sender_contact=sender_contact,
#                 sender_address=sender_address,
#                 sender_pincode=sender_pincode,
#                 receiver_name=receiver_name,
#                 receiver_address=receiver_address,
#                 receiver_pincode=receiver_pincode,
#                 receiver_contact=receiver_contact,
#                 receiver_latitude=latitude,
#                 receiver_longitude=longitude,
#                 modified_receiver_pincode=modified_pincode,
#             )

#             return Response(
#                 {
#                     "message": "Post data processed successfully.",
#                     "data": ScannedPostSerializer(post_data).data,
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as e:
#             return Response(
#                 {"error": f"Failed to process images: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


# class PostDataViewSet(viewsets.ModelViewSet):
#     queryset = PostData.objects.all()  # Retrieve all records
#     serializer_class = ScannedPostSerializer

#     def create(self, request, *args, **kwargs):
#         """
#         Override the create method to disable POST requests.
#         """
#         return Response(
#             {"error": "POST requests are not allowed on this endpoint."},
#             status=status.HTTP_405_METHOD_NOT_ALLOWED
#         )

import os
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from PIL import Image
from .models import PostData, PincodeMapping
import requests
from .serializers import ScannedPostSerializer

from .utils import (
    extract_details,
    get_address_details,
    get_pincode_from_scrap,
    azure_ocr_extract,
    # send_whatsapp_message,
    send_whatsapp_notification,
    
)

# def handle_notification(receiver_contact, receiver_address, receiver_pincode, modified_pincode, merged_reciever_pincode):
#     """
#     Handle WhatsApp notifications for different cases.
#     """
#     print(f"Receiver Contact: {receiver_contact}")
#     print(f"Receiver Address: {receiver_address}")
#     print(f"Receiver Pincode: {receiver_pincode}")
#     print(f"Modified Pincode: {modified_pincode}")
#     print(f"Merged Pincode: {merged_reciever_pincode}")
#     if not receiver_contact:
#         return {"error": "Receiver contact is required to send notifications."}

#     if not receiver_address and not receiver_pincode and receiver_contact:
#         # Case 4: Only phone number provided
#         message = "Hello, we noticed incomplete details for your delivery. Please fill out this form: https://example.com/form"
#         send_whatsapp_message(f"whatsapp:{receiver_contact}", message)
#         return {"case": 4, "message": "Form link sent to user."}

#     if not receiver_address and receiver_pincode:
#         # Case 3: Missing address
#         final_pincode = modified_pincode or merged_reciever_pincode or receiver_pincode
#         message = (
#             f"Hello, we have your pincode as {final_pincode}, but your address is missing. "
#             f"Please complete your details here: https://example.com/form"
#         )
#         send_whatsapp_message(f"whatsapp:{receiver_contact}", message)
#         return {"case": 3, "message": "Form link sent to user for missing address."}

#     if not receiver_pincode:
#         # Case 2: Missing pincode
#         final_pincode = modified_pincode or merged_reciever_pincode
#         if final_pincode:
#             message = (
#                 f"Hello, based on your address, the corrected pincode is {final_pincode}. "
#                 f"Please confirm if this is correct."
#             )
#         else:
#             message = (
#                 "Hello, we couldn't determine your pincode. Please confirm your details here: https://example.com/form"
#             )
#         send_whatsapp_message(f"whatsapp:{receiver_contact}", message)
#         return {"case": 2, "message": "User notified about corrected pincode."}

#     if not modified_pincode and not merged_reciever_pincode:
#         # Case 1: All fields are null
#         message = (
#             f"Hello, we have your contact and address: {receiver_address}. "
#             f"However, no pincode is available. Please provide it to ensure timely delivery."
#         )
#         send_whatsapp_message(f"whatsapp:{receiver_contact}", message)
#         return {"case": 1, "message": "User notified about missing pincode."}

#     return {"error": "Unhandled case."}

# Helper Function to Check Merged Pincode
def check_merged_pincode(pincode):
    mapping = PincodeMapping.objects.filter(old_pincode=pincode).first()
    return mapping.new_pincode if mapping else pincode

# Helper Function to Save Uploaded Files
def handle_uploaded_file(image, image_path):
    try:
        with open(image_path, "wb") as temp_file:
            for chunk in image.chunks():
                temp_file.write(chunk)
    except Exception as e:
        raise IOError(f"Error saving file {image_path}: {str(e)}")

@method_decorator(csrf_exempt, name='dispatch')
class ProcessPostDataView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Retrieve the uploaded files
        image1 = request.FILES.get('senderImage')
        image2 = request.FILES.get('receiverImage')

        # Debugging: Log request details
        print(f"Request method: {request.method}")
        print(f"Request files: {request.FILES}")
        print(f"Request data: {request.data}")

        if not image1 or not image2:
            return Response(
                {"error": "Both fields (senderImage and receiverImage) are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Define paths to temporarily save the images
        image_path1 = os.path.join(settings.MEDIA_ROOT, 'post_images', image1.name)
        image_path2 = os.path.join(settings.MEDIA_ROOT, 'post_images', image2.name)

            # url = "https://22f3-49-249-229-42.ngrok-free.app/process-image/"
            # image_path = "/path/to/your/image.jpg"

            # with open(image_path, "rb") as image_file:
            #     response = requests.post(url, files={"image": image_file})

            # if response.status_code == 200:
            #     extracted_text = response.json()["extracted_text"]
            #     print(extracted_text)
            # else:
            #     print("Error:", response.status_code)
        # Ensure the directory exists
        os.makedirs(os.path.dirname(image_path1), exist_ok=True)
        os.makedirs(os.path.dirname(image_path2), exist_ok=True)

        # Save the images to the server
        try:
            handle_uploaded_file(image1, image_path1)
            handle_uploaded_file(image2, image_path2)
        except Exception as e:
            return Response(
                {"error": f"Failed to save uploaded files: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Verify the images
        allowed_formats = ["JPEG", "PNG", "JPG"]
        try:
            for image_path in [image_path1, image_path2]:
                with Image.open(image_path) as img:
                    img_format = img.format.upper()
                    if img_format not in allowed_formats:
                        raise ValueError(f"Unsupported image format: {img_format}")
                    img.verify()  # Validate the image
                    print(f"Valid image: {image_path} with format {img_format}")
        except Exception as e:
            return Response(
                {"error": f"Invalid image file: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process images and extract text
        try:
            try:
                sender_text = azure_ocr_extract(image_path1)
                print(f"Sender Text: {sender_text}")
                receiver_text = azure_ocr_extract(image_path2)
                print(f"Receiver Text: {receiver_text}")
            except Exception as e:
                return Response(
                    {"error": f"Failed to extract text from images: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


            try:
                sender_details = extract_details(sender_text)
                receiver_details = extract_details(receiver_text)
            except Exception as e:
                return Response(
                {"error": f"Failed to extract details from text: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

            sender_name = sender_details.get("name")
            sender_address = sender_details.get("address")
            sender_pincode = sender_details.get("pincode")
            sender_contact = sender_details.get("contact")

            receiver_name = receiver_details.get("name")
            receiver_address = receiver_details.get("address")
            receiver_pincode = receiver_details.get("pincode")
            receiver_contact = receiver_details.get("contact")

            # Get geocoded address details
            fetched_address = get_address_details(receiver_address)
            fetched_pincode = fetched_address.get("pincode")
            latitude = fetched_address.get("latitude")
            longitude = fetched_address.get("longitude")

            # Fallback to scraping if geocoding fails
            if fetched_pincode is None:
                fetched_pincode = get_pincode_from_scrap(receiver_address)

            # Handle modified pincode logic
            modified_pincode = None
            if fetched_pincode and fetched_pincode != receiver_pincode:
                modified_pincode = fetched_pincode
                send_whatsapp_notification(     
                   sender_name = sender_name,
                   sender_contact=sender_contact,
                   receiver_address=receiver_address,
                   provided_pincode=receiver_pincode,
                   modified_pincode=modified_pincode
               )
            merged_reciever_pincode = None
            if modified_pincode:
                merged_pincode = check_merged_pincode(modified_pincode)
                if merged_pincode != modified_pincode:
                    merged_reciever_pincode = merged_pincode
            merged_pincode = check_merged_pincode(receiver_pincode)
            if merged_pincode != receiver_pincode:
                merged_reciever_pincode = merged_pincode

            
            # response = handle_notification(
            #     receiver_contact,
            #     receiver_address,
            #     receiver_pincode,
            #     modified_pincode,
            #     merged_reciever_pincode
            # )
            
            
            # Save post data
            post_data = PostData.objects.create(
                image1=image1,
                image2=image2,
                sender_name=sender_name,
                sender_contact=sender_contact,
                sender_address=sender_address,
                sender_pincode=sender_pincode,
                receiver_name=receiver_name,
                receiver_address=receiver_address,
                receiver_pincode=receiver_pincode,
                receiver_contact=receiver_contact,
                receiver_latitude=latitude,
                receiver_longitude=longitude,
                modified_receiver_pincode=modified_pincode,
                merged_reciever_pincode = merged_reciever_pincode,

            )

    # Serialize the saved data
            serialized_data = ScannedPostSerializer(post_data, context={'request': request}).data


    # Return a JSON response
            print("Serialized Data:", serialized_data)

            return Response(
        {
            "message": "Post data processed successfully.",
            "data": serialized_data,
        },
        status=status.HTTP_200_OK,
    )

        except Exception as e:
            return Response(
        {"error": f"Internal Server Error: {str(e)}"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
            
    

class PostDataViewSet(viewsets.ModelViewSet):
    queryset = PostData.objects.all()  # Retrieve all records
    serializer_class = ScannedPostSerializer

    def create(self, request, *args, **kwargs):
        """
        Override the create method to disable POST requests.
        """
        return Response(
            {"error": "POST requests are not allowed on this endpoint."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

from django.http import JsonResponse

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PostData
from twilio.twiml.messaging_response import MessagingResponse

@csrf_exempt
def twilio_whatsapp_webhook(request):
    """
    Handles incoming WhatsApp messages via Twilio for chat validation.
    """
    if request.method == "POST":
        # Parse incoming data
        sender_contact = request.POST.get("From", "").replace("whatsapp:", "").strip()
        reply_text = request.POST.get("Body", "").strip().lower()

        # Fetch the latest post data for this sender
        post_data = PostData.objects.filter(sender_contact=sender_contact).order_by('-created_at').first()

        if not post_data:
            return HttpResponse("No matching post data found.", status=404)

        # Check if the chat is already resolved
        if post_data.chat_status == "resolved":
            # Respond with a message stating the chat is already closed
            response_message = MessagingResponse()
            response_message.message("This chat has already been resolved. No further actions are needed.")
            return HttpResponse(str(response_message), content_type="text/xml")

        # Process user response
        response_message = MessagingResponse()
        if reply_text == "yes":
            # Save response and mark chat as resolved
            post_data.customer_feedback = "Yes"
            post_data.chat_status = "resolved"
            post_data.save()

            response_message.message("Thank you! The pincode has been updated.")
        elif reply_text == "no":
            # Save response and mark chat as resolved
            post_data.customer_feedback = "No"
            post_data.chat_status = "resolved"
            post_data.save()

            response_message.message(
                "We cannot process the change. Please visit your nearest post office to update the address or pincode."
            )
        else:
            # Invalid response: Keep chat status as pending
            response_message.message("Invalid response. Please reply with 'Yes' or 'No'.")

        return HttpResponse(str(response_message), content_type="text/xml")

    return HttpResponse("Invalid request method.", status=405)