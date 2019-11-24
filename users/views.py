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
from django.db.utils import IntegrityError

from .models import *


from .forms import *
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

class RelationshipView(TemplateView):
    template_name='relationships.html'
    def get(self,request,id1,id2):
        form=TransactionFriendForm()
        try:
            relid1=Relationship.objects.filter(active_id__id=id1).filter(receiver_id__id=id2)
            relid2=Relationship.objects.filter(active_id__id=id2).filter(receiver_id__id=id1)

        except:
            print("Exception")

        relationship12=relid1[0]
        relationship21=relid2[0]
        active_user=CustomUser.objects.filter(id=id1)
        receive_user=CustomUser.objects.filter(id=id2)
        active_user=active_user[0]
        receive_user=receive_user[0]
        non_group_transactions=Accounts.objects.filter(relation_id=relationship12)|Accounts.objects.filter(relation_id=relationship21)
        non_group_transactions=non_group_transactions.filter(trans_id__group_or_no=False)
        non_group_transactions=non_group_transactions.order_by('-trans_id__date')
        args={'active_user':active_user,'receive_user':receive_user,'relationship12':relationship12,'relationship21':relationship21,'form':form,'non_group_transactions':non_group_transactions}

        return render(request=request, template_name=self.template_name, context=args)

    def post(self,request,id1,id2):
        form=TransactionFriendForm(request.POST)
        if form.is_valid():
            trans_amt=int(form.cleaned_data['trans_amt'])
            trans_choice=form.cleaned_data['trans_choice']
            tag=form.cleaned_data['trans_tag']
            if trans_choice=='receive':
                trans_amt= -trans_amt
            trans_text=form.cleaned_data['trans_text']
            try :
                relid1=Relationship.objects.filter(active_id__id=id1).filter(receiver_id__id=id2)
                relid2=Relationship.objects.filter(active_id__id=id2).filter(receiver_id__id=id1)

            except:
                print("Error")
            relationship12=relid1[0]
            relationship21=relid2[0]
            active_user=CustomUser.objects.filter(id=id1)
            receive_user=CustomUser.objects.filter(id=id2)
            active_user=active_user[0]
            receive_user=receive_user[0]
            relationship12.net_balance=relationship12.net_balance+trans_amt
            relationship12.save()
            t=Transaction(active_id=active_user,amt_paid=trans_amt,group_or_no=False,trans_name=trans_text,trans_tag=tag)

            t.save()
            a=Accounts(trans_id=t,relation_id=relationship12,amt_exchanged=trans_amt)
            a.save()
            print(a.trans_id.trans_name)
            non_group_transactions=Accounts.objects.filter(relation_id=relationship12)|Accounts.objects.filter(relation_id=relationship21)
            non_group_transactions=non_group_transactions.filter(trans_id__group_or_no=False)
            non_group_transactions=non_group_transactions.order_by('-trans_id__date')
            print(non_group_transactions)


        args={'active_user':active_user,'receive_user':receive_user,'relationship12':relationship12,'relationship21':relationship21,'form':form,'non_group_transactions':non_group_transactions}
        return render(request=request, template_name=self.template_name, context=args)
