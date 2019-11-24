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
from django.db.models import Sum
from django.http import HttpResponseRedirect, HttpResponse

from .models import *


from .forms import *
#Sign up

def subractdict(grp_list,dict12,dict21):
    d={}
    for i in grp_list:
        print
        d[i]=dict21.get(i.id,0)-dict12.get(i.id,0)
    return d


def convertdict(data):
    dicto={}
    for i in data:
        dicto[i['trans_id__group_num']]=i['amt_exchanged__sum']

    return dicto


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
        form = CustomUserChangeForm(data=request.POST, files=request.FILES,instance=request.user)
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
        friend_form = FriendForm()
        users = Relationship.objects.filter(active_id__id=id)
        args = {"users" : users, 'friend_form':friend_form}
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

        all_t_12=Accounts.objects.filter(relation_id=relationship12)
        all_t_21=Accounts.objects.filter(relation_id=relationship21)
        all_transactions=all_t_12|all_t_21
        all_t_12_sum=all_t_12.aggregate(Sum('amt_exchanged'))['amt_exchanged__sum']
        all_t_21_sum=all_t_21.aggregate(Sum('amt_exchanged'))['amt_exchanged__sum']
        if all_t_21_sum==None:
            all_t_21_sum=int(0)
        if all_t_12_sum==None:
            all_t_12_sum=int(0)


        non_group_transactions=all_transactions.filter(trans_id__group_or_no=False)
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
            relationship12.save()
            t=Transaction(active_id=active_user,amt_paid=trans_amt,group_or_no=False,trans_name=trans_text,trans_tag=tag)

            t.save()
            a=Accounts(trans_id=t,relation_id=relationship12,amt_exchanged=trans_amt)
            a.save()
            all_t_12=Accounts.objects.filter(relation_id=relationship12)
            all_t_21=Accounts.objects.filter(relation_id=relationship21)
            all_transactions=all_t_12|all_t_21
            all_t_12_sum=all_t_12.aggregate(Sum('amt_exchanged'))['amt_exchanged__sum']
            all_t_21_sum=all_t_21.aggregate(Sum('amt_exchanged'))['amt_exchanged__sum']
            if all_t_21_sum==None:
                all_t_21_sum=int(0)
            if all_t_12_sum==None:
                all_t_12_sum=int(0)
            common_groups=Group.objects.filter(members=active_user).filter(members=receive_user)
            group12dict=all_t_12.values('trans_id__group_num').annotate(Sum('amt_exchanged'))
            group21dict=all_t_21.values('trans_id__group_num').annotate(Sum('amt_exchanged'))
            dict12=convertdict(group12dict)
            dict21=convertdict(group21dict)
            final_group=subractdict(common_groups,dict12,dict21)
            print(final_group)
            non_group_transactions=all_transactions.filter(trans_id__group_or_no=False)
            non_group_transactions=non_group_transactions.order_by('-trans_id__date')
            balance=all_t_21_sum-all_t_12_sum


        args={'balance':balance,'active_user':active_user,'receive_user':receive_user,'relationship12':relationship12,'relationship21':relationship21,'form':form,'non_group_transactions':non_group_transactions,'final_group':final_group}
        return render(request=request, template_name=self.template_name, context=args)

def settle_friend(request,id1,id2):

    pass