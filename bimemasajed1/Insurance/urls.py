from django.urls import path 
from . import views
urlpatterns=[
    path('',views.showdata_view,name='showdata'),
    path ('alldata/',views.alldata_view,name='alldata'),
]