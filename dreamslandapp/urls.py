from django.urls import path
from . import views  

urlpatterns = [
    path('', views.loginpage, name='loginpage'),
    path('login', views.login, name='login'),
    path('admindashboard', views.admindashboard, name='admindashboard'),
    path('analytics', views.analytics, name='analytics'),
    path('logout', views.logout, name='logout'),
    path('properties', views.properties, name='properties'),
    path('properties/delete/<str:property_id>/', views.delete_property, name='delete_property'),
    path('properties/update/', views.update_property, name='update_property'),
]
