from django.urls import path
from . import views


urlpatterns = [
    #path('login/', views.my_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('friend/<id>', views.FriendTabView.as_view(), name='friend'),
    path('friend/', views.SignUpView.as_view(), name='friend'),
]