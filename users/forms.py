from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser,Transaction
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
    username=forms.CharField(max_length=150)

class TransactionGroupForm(forms.Form):
    CHOICES=(('Other','Other'),('Work','Work'),('Personal','Personal'))
    trans_tag=forms.ChoiceField(label='Add Transaction Tag:',choices=CHOICES,widget=forms.Select(),required=False)


    
class TransactionFriendForm(forms.Form):
	trans_amt=forms.IntegerField(label="Add Transaction Amount:")
	C=[('pay','pay'),('receive','receive')]
	trans_choice=forms.ChoiceField(choices=C,widget=forms.RadioSelect)
	trans_text=forms.CharField(label="Transaction Name:")
	CHOICES=(('Other','Other'),('Work','Work'),('Personal','Personal'))
	trans_tag=forms.ChoiceField(label='Add Transaction Tag:',choices=CHOICES,widget=forms.Select(),required=False)

