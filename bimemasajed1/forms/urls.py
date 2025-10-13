from django.urls import path
from . import views
urlpatterns=[
    path ('signin/', views.signin, name="signin"),
    path ('login/', views.login, name='login'),
    path ('logout/', views.logout, name='logout'),
    path ('mainform/', views.MainRegistration, name='mainform'),
    path ('personform/', views.PersonInfo, name='personform'),
    path ('buildform/', views.BuildingInformation, name='buildform'),
    path ('boardform/', views.TrusteesBoard, name='boardform'),
]