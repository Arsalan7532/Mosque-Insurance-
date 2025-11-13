from django.urls import path 
from . import views
urlpatterns=[
    path('',views.newinsurance_view,name='insurance'),
    path ('alldata/',views.alldata_json,name='alldata'),
    path ('myinsurance/',views.myinsurance,name='myinsurance'),
]