# users/views.py
from django.urls import reverse_lazy
from django.db.utils import IntegrityError
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from .models import CustomUser, Relationship, Group
from django.http import HttpResponseRedirect
from .forms import CustomUserCreationForm, FriendForm

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class FriendTabView(TemplateView):
    template_name = "friendslist.html"

    def get(self, request, id):
        friend_form = FriendForm()
        users = Relationship.objects.filter(active_id__id=id)
        groups = Group.objects.filter(members__id=id)
        args = {"users" : users,
                'user_id' : id,
                "groups" : groups,
                'friend_form':friend_form,
            }
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
        users = Relationship.objects.filter(active_id__id=id)
        args = {"users" : users, 'friend_form':friend_form, 'grp_form':grp_form}
        return render(request=request, template_name=self.template_name, context=args)

class CreateGroupView(TemplateView):
    template_name = 'create_group.html'

    def get(self, request, id):
        relationships = Relationship.objects.filter(active_id__id=id)
        args = {'relationships':relationships}
        return render(request=request,template_name=self.template_name,context=args)

    def post(self, request, id):
        grp_name = request.POST['grp_name']
        if 'list_id' in request.POST:                
            friend_ids = request.POST.getlist('list_id')
            for i in range(len(friend_ids)): ## making everyone friends in a group
                for j in range(i+1, len(friend_ids)):
                    if Relationship.objects.filter(active_id__id=int(friend_ids[i]), receiver_id__id=int(friend_ids[j])).count() == 0:
                        user1 = CustomUser.objects.get(id=int(friend_ids[i]))
                        user2 = CustomUser.objects.get(id=int(friend_ids[j]))
                        r = Relationship(active_id=user1, receiver_id=user2)
                        r.save()
                        r = Relationship(active_id=user2, receiver_id=user1)
                        r.save()
            g = Group(grp_name=grp_name)
            g.save()
            g.members.add(CustomUser.objects.get(id=id))
            for fr_id in friend_ids :
                g.members.add(CustomUser.objects.get(id=int(fr_id)))
        return HttpResponseRedirect('../friend/%s' % id)


class CreateTransactionView(TemplateView):
    template_name = 'create_transaction.html'

    def get(self, request, grp_id):
        relationships = Relationship.objects.filter(active_id__id=grp_id)
        groups = Group.objects.filter(members__id=grp_id)
        args = {
            'user_id' : grp_id,
            'relationships' : relationships,
            'groups' : groups,
        }
        return render(request=request,template_name=self.template_name, context=args)