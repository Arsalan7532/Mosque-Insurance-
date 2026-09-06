from django.urls import path
from . import views
urlpatterns=[
    #path('send-to-insurance/',views.SendToInsuranceAPIView.as_view(),name='sendapi')
    path ('RequestBime/',views.RequestQuoteAPIView.as_view(),name='RequestApi')
    ]