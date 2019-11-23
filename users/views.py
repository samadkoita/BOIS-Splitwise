# users/views.py
from django.urls import reverse_lazy
from django.db.utils import IntegrityError
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from .models import CustomUser, Relationship, Group

from .forms import CustomUserCreationForm, FriendForm, GroupForm

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

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

