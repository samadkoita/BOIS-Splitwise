from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'firstname','lastname', 'email')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'firstname','lastname', 'email')

class FriendForm(forms.Form):
    username = forms.CharField(max_length=150)

class GroupForm(forms.Form):
    grp_name = forms.CharField(max_length=150)
    number_friends = forms.IntegerField(initial=1)