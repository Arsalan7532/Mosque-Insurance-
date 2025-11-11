from django.urls import path
from . import views
urlpatterns=[
    path ('signin/', views.signin, name="signin"),
    path ('login/', views.login, name='login'),
    path ('logout/', views.logout, name='logout'),
    path ('mainform/', views.MainRegistration_view, name='mainform'),
    path ('personform/', views.PersonInfo_view, name='personform'),
    path ('buildform/', views.BuildingInformation_view, name='buildform'),
    path ('boardform/', views.trusteesboard_view, name='boardform'),
]