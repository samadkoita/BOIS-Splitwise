from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#This has all the URLs related to signing ,sein. The login and logout url is mentioned in the m

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('friend/<id>', views.FriendView, name='friend'),
    path('friend/', views.SignUpView.as_view(), name='friend'),
    path('password/', views.change_password, name='change_password'),
    path('update/',views.profileupdate,name = 'update')
]

#r'^(?P<pk>\d+)/$'