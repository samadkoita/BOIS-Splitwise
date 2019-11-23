from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = False

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('firstname','lastname', 'email','avatar')
    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['firstname'].required = False
        self.fields['lastname'].required = False
        self.fields['avatar'].required = False

        

class FriendForm(forms.Form):
    username = forms.CharField(max_length=150)

class GroupForm(forms.Form):
    grp_name = forms.CharField(max_length=150)
    number_friends = forms.IntegerField(initial=1)