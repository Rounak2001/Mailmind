from django.urls import path, include
from .views import ProcessPostDataView, PostDataViewSet
from rest_framework.routers import DefaultRouter
from .views import twilio_whatsapp_webhook


router = DefaultRouter()
router.register(r'post-data', PostDataViewSet)

urlpatterns = [
    path('upload/', ProcessPostDataView.as_view(), name='post-data'),
    path('', include(router.urls)),
    path('twilio/whatsapp-webhook/', twilio_whatsapp_webhook, name='twilio-whatsapp-webhook'),  
]
    # path('twilio/whatsapp-webhook/', twilio_whatsapp_webhook, name='twilio-whatsapp-webhook'),

