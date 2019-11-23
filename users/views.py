# users/views.py
from django.urls import reverse_lazy
from django.db.utils import IntegrityError
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from .models import CustomUser, Relationship

from .forms import CustomUserCreationForm, FriendForm

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class FriendTabView(TemplateView):
    template_name = "friendslist.html"

    def get(self, request, id):
        form = FriendForm()
        users = Relationship.objects.filter(active_id__id=id)
        args = {"users" : users, 'form':form}
        return render(request=request, template_name=self.template_name, context=args)

    def post(self, request, id):
        form = FriendForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            friends = CustomUser.objects.filter(email=email)
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
        form = FriendForm()
        users = Relationship.objects.filter(active_id__id=id)
        args = {"users" : users, 'form':form}
        return render(request=request, template_name=self.template_name, context=args)

