from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .serializers import ScannedPostSerializer
from .models import PostData
from .utils import (
    extract_details,
    get_address_details,
    get_pincode_from_scrap,
)

class ProcessPostDataView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Save the image and sender address
        # image = request.FILES.get('image')
        text1 = request.data.get('text1')
        text2 = request.data.get('text2')

        if  not text1 or not text2:
            return Response({"error": "All fields (image, text1, text2) are required."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Step 4 segregate sender or reciever
        if "from:" in text1.lower():
            sender_text = text1.replace("from:", "").strip()
            receiver_text = text2.replace("to:", "").strip()
        else:
            sender_text = text2.replace("from:", "").strip()
            receiver_text = text1.replace("to:", "").strip()

        # Step 5 Extract all the details
        sender_details = extract_details(sender_text)
        receiver_details = extract_details(receiver_text)

        sender_name = sender_details.get("name")
        sender_address = sender_details.get("address")
        sender_pincode = sender_details.get("pincode")
        sender_contact = sender_details.get("contact")

        receiver_name = receiver_details.get("name")
        receiver_address = receiver_details.get("address")
        receiver_pincode = receiver_details.get("pincode")
        receiver_contact = receiver_details.get("contact")

        # Step 6 Get address details
        fetched_address = get_address_details(receiver_address)
        fetched_pincode = fetched_address.get("pincode")
        latitude = fetched_address.get("latitude")
        longitude = fetched_address.get("longitude")

        # Step 7 Search pincode from web
        if fetched_pincode == None:
            fetched_pincode = get_pincode_from_scrap(receiver_address)

        # Step 8 Notification and new pincode save
        modified_pincode = None
        if fetched_pincode and fetched_pincode != receiver_pincode:
            modified_pincode = fetched_pincode
            
            # step 9 Merged pincode concept
    #         send_whatsapp_notification(
    #             sender_name = sender_name,
    #             sender_contact=sender_contact,
    #             receiver_address=receiver_address,
    #             provided_pincode=receiver_pincode,
    #             modified_pincode=modified_pincode
    # ) 
        # step 10 merge pincode
        # Merge Pincode concept 
        # if not fetched_pincode:
       
        # step 11 Save the data
        post_data = PostData.objects.create(
            # image=image,
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
            modified_receiver_pincode=modified_pincode
        )
        post_data = request.data
        return Response(
            {
                "message": "Post data processed successfully.",
                "data": post_data  
            }, 
            status=status.HTTP_200_OK
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
    