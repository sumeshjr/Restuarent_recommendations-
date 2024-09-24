
from django.urls import path 
from .views import *

urlpatterns = [
     path('', index, name='index'),
     path('login_page/', login_page, name='login_page'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('history/', history, name='history'),
    path('graph/', graph, name='graph'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('contact/', contact, name='contact'),
    path('recommend/', recommend, name='recommend'),
    path('recommendations/', recommendations, name='recommendations'),
    path('about/', about, name='about'),
    path('contact_page/', contact_page, name='contact_page'),
    path('users/', all_users, name='all_users'),
    path('users/update/<int:user_id>/', update_user, name='update_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('all_searched_restaurants/', all_searched_restaurants, name='all_searched_restaurants'),
    path('user_search_graph/', user_search_graph, name='user_search_graph'),
    path('maindash/', maindash, name='maindash'),
    path('user_search/', user_search, name='user_search'),
    path('download/history/', download_user_history, name='download_user_history'),
    path('profile/', user_profile, name='user_profile'),
    path('change-password/', change_password, name='change_password'),
    path('all_contacts/', all_contacts, name='all_contacts'),
    path('chat_home/', chat_home, name='chat_home'),
]