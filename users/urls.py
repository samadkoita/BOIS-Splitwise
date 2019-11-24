from django.urls import path
from . import views


urlpatterns = [
    #path('login/', views.my_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('friend/<int:id>', views.FriendTabView.as_view(), name='friend'),
    # path('friend/<int:id>/create_transaction/<int:grp_id>', views.CreateTransactionView.as_view(), name='create_transaction'),
    path('friend/', views.SignUpView.as_view(), name='friend'),
    path('create_group/<int:id>', views.CreateGroupView.as_view(), name='create_group'),
    path('create_transaction/<int:grp_id>', views.CreateTransactionView.as_view(), name='create_transaction'),
]