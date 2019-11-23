# users/views.py
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.contrib.sessions import *
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required

from .models import CustomUser, Relationship

from .forms import CustomUserCreationForm,CustomUserChangeForm
#Sign up
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class UpdatedView(UpdateView):
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('login')
    template_name = 'update_details.html'
    def get_object(self):
        return self.request.user
@login_required
def profileupdate(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'update_details.html', {'form': form})



def viewupdate(request,id):
    instance = instance = get_object_or_404(CustomUser, id=id)
    form = UpdateView(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('next_view')
    return render(request, 'update_details.html', {'form': form}) 




#Change password once logged in
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })



def FriendView(request, id):
    template_name = "friendslist.html"
    users = Relationship.objects.filter(active_id__id=id)
    print(id)
    args = {"users" : users}
    return render(request=request, template_name=template_name, context=args)