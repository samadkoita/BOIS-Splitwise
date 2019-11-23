# users/views.py
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from .models import CustomUser, Relationship, Group
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.contrib.sessions import *
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from .forms import CustomUserCreationForm,CustomUserChangeForm,FriendForm,GroupForm

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
  
class FriendTabView(TemplateView):
    template_name = "friendslist.html"

    def get(self, request, id):
        friend_form = FriendForm()
        grp_form = GroupForm()
        users = Relationship.objects.filter(active_id__id=id)
        groups = Group.objects.filter(members__id=id)
        # print(groups)
        args = {"users" : users, 'friend_form':friend_form, 'grp_form':grp_form}
        return render(request=request, template_name=self.template_name, context=args)

    def post(self, request, id):
        form = FriendForm(request.POST)
        if form.is_valid():
            if 'friend' in request.POST :
                username = form.cleaned_data['username']
                friends = CustomUser.objects.filter(username=username)
                if len(friends) == 1:
                    if friends[0].id != int(id) :
                        try:
                            user = CustomUser.objects.get(id=id)
                            r = Relationship(active_id=user, receiver_id=friends[0])
                            r.save()
                            r = Relationship(active_id=friends[0], receiver_id=user)
                            r.save()
                        except (IntegrityError,CustomUser.DoesNotExist) as e:
                            print(e)
            elif 'group' in request.POST :
                pass
        friend_form = FriendForm()
        grp_form = GroupForm()
        users = Relationship.objects.filter(active_id__id=id)
        args = {"users" : users, 'friend_form':friend_form, 'grp_form':grp_form}
        return render(request=request, template_name=self.template_name, context=args)

