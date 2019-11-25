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
    path('group/<int:grp_id>/<int:id>/', views.GroupView.as_view(), name='group'),
    path('group/<int:grp_id>/<int:id>/settle/', views.settle_group, name='settle_group'),
    path('create_group/<int:id>/', views.CreateGroupView.as_view(), name='create_group'),
    path('create_transaction/<int:grp_id>/'
    , views.CreateTransactionView.as_view(), name='create_transaction'),
    path('create_transaction/<int:grp_id>/<int:id>/'
    , views.CreateTransactionView.as_view(), name='create_transaction'),
    path('friend/<id1>/<id2>/',views.RelationshipView.as_view(),name='relationship'),
    path('friend/<id1>/<id2>/settle/',views.settle_friend,name='settle_friend'),
    path('insight/timeseries/<id>',views.TimeSeriesViews, name = 'times'),#
    path('insight/piechart/data/<id>',views.piMe, name = 'proc1'),
    path('insight/friends/<id>',views.ListFriends,name = 'friendslist'),# 
    path('insight/pifriends/<id1>/<id2>',views.PiFriends,name = 'pifriends'),#
    path('insight/piechart',views.json_example,name='piechart'),#
    path('insight/bargraph/friends/<id>',views.BarFriends,name = 'bargraph1'),#
    path('export/xls/<id>', views.export_users_xls, name='export_users_xls'),
    path('insight/bargraphoptions/<id>',views.BarGroups,name = 'bargroup'),
]
#r'^(?P<pk>\d+)/$'
