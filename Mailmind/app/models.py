from django.db import models

class PostData(models.Model):
    image = models.ImageField(upload_to='post_images/')
    sender_name = models.CharField(max_length=255, null=True, blank=True)
    sender_contact = models.CharField(max_length=20, null=True, blank=True)
    sender_address = models.TextField(null=True, blank=True)
    sender_pincode = models.CharField(max_length=6, null=True, blank=True)
    receiver_name = models.CharField(max_length=255, null=True, blank=True)
    receiver_contact = models.CharField(max_length=20, null=True, blank=True)
    receiver_address = models.TextField(null=True, blank=True)
    receiver_pincode = models.CharField(max_length=6, null=True, blank=True)
    modified_receiver_pincode = models.CharField(max_length=6, null=True, blank=True)
    receiver_latitude = models.TextField(null=True, blank=True)
    receiver_longitude = models.TextField(null=True, blank=True)
    customer_feedback = models.TextField(null=True, blank=True)
    chat_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),  # Waiting for user response
            ('resolved', 'Resolved')  # Chat completed
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post from {self.sender_name}"
