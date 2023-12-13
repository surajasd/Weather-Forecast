from django.urls import path
from . import views
# from .views import check_favcity


urlpatterns = [
    path('', views.default_page, name='default_page'),  # Redirect the root URL to the login page
    path('index/', views.index, name='index'),
    path('rem/<int:id>', views.remove, name='remove'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('index2/', views.index2, name='index2'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('add_to_favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('logout/', views.logout, name='logout'),
    # path('cf/',check_favcity, name='check_favcity'),
]
