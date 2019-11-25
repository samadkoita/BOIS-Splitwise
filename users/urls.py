from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#This has all the URLs related to signing ,sein. The login and logout url is mentioned in the m

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('password/', views.change_password, name='change_password'),
    path('update/',views.profileupdate,name = 'update'),
    path('friend/<id>/', views.FriendTabView.as_view(), name='friend'),
    path('friend/', views.SignUpView.as_view(), name='friend'),
    path('create_group/<int:id>/', views.CreateGroupView.as_view(), name='create_group'),
    path('friend/<id1>/<id2>/',views.RelationshipView.as_view(),name='relationship'),
    path('friend/<id1>/<id2>/settle/',views.settle_friend,name='settle_friend'),
]
#r'^(?P<pk>\d+)/$'
