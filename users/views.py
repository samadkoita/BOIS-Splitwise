# users/views.py
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse,JsonResponse
from django.contrib.sessions import *
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from django.db.models import Sum
from django.http import HttpResponseRedirect, HttpResponse
import json
from .models import *
from datetime import datetime, timedelta

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

def convertdict2(data):
    dicto={}
    for i in data:
        dicto[i['trans_id']]=i['amt_exchanged__sum']
    return dicto

def convertdict3(data,inp):
    dicto={}
    for i in data:
        dicto[i[inp]]=i['amt_exchanged__sum']

    return dicto

def friend_balance(id1,id2):
    if True:
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

        balance=all_t_21_sum-all_t_12_sum
        return balance

def friend_non_group_balance(id1,id2):
    if True:
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
        all_t_12=Accounts.objects.filter(relation_id=relationship12).filter(trans_id__group_or_no=False)
        all_t_21=Accounts.objects.filter(relation_id=relationship21).filter(trans_id__group_or_no=False)
        all_transactions=all_t_12|all_t_21
        all_t_12_sum=all_t_12.aggregate(Sum('amt_exchanged'))['amt_exchanged__sum']
        all_t_21_sum=all_t_21.aggregate(Sum('amt_exchanged'))['amt_exchanged__sum']
        if all_t_21_sum==None:
            all_t_21_sum=int(0)
        if all_t_12_sum==None:
            all_t_12_sum=int(0)
        non_group_transactions=all_transactions.filter(trans_id__group_or_no=False)
        non_group_transactions=non_group_transactions.order_by('-trans_id__date')
        balance=all_t_21_sum-all_t_12_sum
        return balance,non_group_transactions

def group_settling_function(id,grp_id):

    curr=Group.objects.get(pk=grp_id)
    s=CustomUser.objects.get(pk=id)
    student_set=curr.members.all()
    temp1=Accounts.objects.filter(trans_id__group_num=curr).filter(relation_id__active_id__id=id)
    temp2=Accounts.objects.filter(trans_id__group_num=curr).filter(relation_id__receiver_id__id=id)
    temp=temp1|temp2
    given_trans=temp.values('relation_id__active_id__id').annotate(Sum('amt_exchanged'))
    taken_trans=temp.values('relation_id__receiver_id__id').annotate(Sum('amt_exchanged'))
    givendict=convertdict3(given_trans,'relation_id__active_id__id')
    takendict=convertdict3(taken_trans,'relation_id__receiver_id__id')
    person_owes_dict=subractdict(student_set,givendict,takendict)
    person_owes_dict.pop(s)
    return person_owes_dict

def get_people_balance(grp_id):

    curr=Group.objects.get(pk=grp_id)
    student_set=curr.members.all()
    temp=Accounts.objects.filter(trans_id__group_num=curr)
    given_trans=temp.values('relation_id__active_id__id').annotate(Sum('amt_exchanged'))
    taken_trans=temp.values('relation_id__receiver_id__id').annotate(Sum('amt_exchanged'))
    givendict=convertdict3(given_trans,'relation_id__active_id__id')
    takendict=convertdict3(taken_trans,'relation_id__receiver_id__id')
    person_owes_dict=subractdict(student_set,givendict,takendict)
    return person_owes_dict


def get_person_group_transaction(id,grp_id):
    a=CustomUser.objects.get(id=id)
    T=Transaction.objects.filter(group_or_no=True).filter(group_num__id=grp_id).order_by('-date')
    curr_group_acc=Accounts.objects.filter(trans_id__group_num__id=grp_id)

    given_trans=curr_group_acc.filter(relation_id__active_id__id=id)
    taken_trans=curr_group_acc.filter(relation_id__receiver_id__id=id)

    given_trans=given_trans.values('trans_id').annotate(Sum('amt_exchanged'))
    taken_trans=taken_trans.values('trans_id').annotate(Sum('amt_exchanged'))
    # For each transaction, show the amount the person owes
    givendict=convertdict2(given_trans)
    takendict=convertdict2(taken_trans)
    net_dict_transaction=subractdict(T,givendict,takendict)
    # For Each Person in the Group, Get the Amount the Person Owes


    return net_dict_transaction

def get_groups_balance(id1,id2):
    if True:
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
        all_t_12=Accounts.objects.filter(relation_id=relationship12).filter(trans_id__group_or_no=True)
        all_t_21=Accounts.objects.filter(relation_id=relationship21).filter(trans_id__group_or_no=True)
        if True:

            common_groups=Group.objects.filter(members=active_user).filter(members=receive_user)
            group12dict=all_t_12.values('trans_id__group_num').annotate(Sum('amt_exchanged'))
            group21dict=all_t_21.values('trans_id__group_num').annotate(Sum('amt_exchanged'))
            dict12=convertdict(group12dict)
            dict21=convertdict(group21dict)
            final_group=subractdict(common_groups,dict12,dict21)
            return final_group


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
        groups = Group.objects.filter(members__id=id)
        args = {"users" : users, 'friend_form':friend_form,'groups':groups}
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
        return HttpResponseRedirect('../../friend/%s' % id)

class CreateTransactionView(TemplateView):
    template_name = 'create_transaction.html'

    def get(self, request, grp_id, id):
        relationships = Relationship.objects.filter(active_id__id=id)
        group = Group.objects.get(id=grp_id)
        transaction_tag = TransactionGroupForm()
        members = group.members.all()
        args = {
            'user_id' : grp_id,
            'relationships' : relationships,
            'group' : group,
            'transaction' : transaction_tag,
            'members' : members,
        }
        return render(request=request,template_name=self.template_name, context=args)
    def post(self, request, grp_id, id):
        print(request.POST)
        desc = request.POST['description']
        amount = int(request.POST['amount'])
        tag = request.POST['trans_tag']
        list_vals_inp = request.POST.getlist('list_vals')
        list_vals = []
        list_ids = request.POST.getlist('list_ids')
        for i in range(len(list_vals_inp)) :
            if list_vals_inp[i] == '':
                list_vals.append((0,int(list_ids[i])))
            else:
                list_vals.append((int(list_vals_inp[i]),int(list_ids[i])))
        split_equally = 'split_equally' in request.POST
        s = sum(map(lambda x : x[0] , list_vals))
        if not split_equally and s != amount:
            print("NOOO")
        else:
            if split_equally:
                for i in range(len(list_vals)) :
                    list_vals[i] = (amount//len(list_vals), list_vals[i][1])
            # add in db
            active_user = CustomUser.objects.get(id=id)
            group_num = Group.objects.get(id=grp_id)
            t=Transaction(active_id=active_user,amt_paid=amount,group_or_no=True,trans_name=desc,trans_tag=tag,group_num=group_num)
            t.save()
            for x in list_vals:
                if x[1] == active_user.id:
                    continue
                rel=Relationship.objects.filter(active_id=active_user, receiver_id=x[1])
                rel=rel[0]
                a=Accounts(trans_id=t,relation_id=rel,amt_exchanged=x[0])
                a.save()
        return HttpResponseRedirect('../../../group/%s/%s' % (grp_id,id))

class GroupView(TemplateView):
    template_name = 'group_home.html'

    def get(self, request, grp_id, id):
        group = Group.objects.get(id=grp_id)
        members = group.members.all()
        members = get_people_balance(grp_id)
        transactions = get_person_group_transaction(id,grp_id)
        args={
            'group' : group,
            'transactions' : transactions,
            'members' : members,
        }
        return render(request=request,template_name=self.template_name, context=args)




class RelationshipView(TemplateView):
    template_name='relationships.html'

    def get(self,request,id1,id2):
        form=TransactionFriendForm()
        try:
            relid1=Relationship.objects.filter(active_id__id=id1).filter(receiver_id__id=id2)
            relid2=Relationship.objects.filter(active_id__id=id2).filter(receiver_id__id=id1)


        except Exception as e:
            print("Exception", e)

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
            print(friend_balance(id1,id2))
            print(friend_non_group_balance(id1,id2))
            print(get_groups_balance(id1,id2))
            non_group_transactions=all_transactions.filter(trans_id__group_or_no=False)
            non_group_transactions=non_group_transactions.order_by('-trans_id__date')
            balance=all_t_21_sum-all_t_12_sum
        args={'balance':balance,'active_user':active_user,'receive_user':receive_user,'relationship12':relationship12,'relationship21':relationship21,'form':form,'non_group_transactions':non_group_transactions,'final_group':final_group}
        return render(request=request, template_name=self.template_name, context=args)

def settle_friend(request,id1,id2):

    non_grp_balance = friend_non_group_balance(id1,id2)
    non_group_transactions=non_grp_balance[1]
    non_grp_balance=non_grp_balance[0]
    print(non_group_transactions)
    print(non_grp_balance)
    grp_balance = get_groups_balance(id1,id2)
    print(grp_balance)
    if True:
        if True:
            try :
                relid1=Relationship.objects.filter(active_id__id=id1).filter(receiver_id__id=id2)
                relid2=Relationship.objects.filter(active_id__id=id2).filter(receiver_id__id=id1)
                active_user=CustomUser.objects.filter(id=id1)
                receive_user=CustomUser.objects.filter(id=id2)
                active_user=active_user[0]
                receive_user=receive_user[0]

            except:
                print("Error")
            relationship12=relid1[0]
            relationship21=relid2[0]

    name1=active_user.username+"-Settling-"+receive_user.username+"- Non Group Expenses"
    if non_grp_balance!=0:
        t=Transaction(active_id=active_user,amt_paid=non_grp_balance,group_or_no=False,settling_or_no=True,trans_name=name1)
        t.save()
        a=Accounts(trans_id=t,relation_id=relationship12,amt_exchanged=non_grp_balance)
        a.save()
    for group,amount in grp_balance.items():
        name1=active_user.username+"-Settling-"+receive_user.username+"- "+group.grp_name+" Expenses"
        if amount!=0:
            t=Transaction(active_id=active_user,amt_paid=amount,group_or_no=True,group_num=group,settling_or_no=True,trans_name=name1)
            t.save()
            a=Accounts(trans_id=t,relation_id=relationship12,amt_exchanged=amount)
            a.save()
    form=TransactionFriendForm()
    balance=friend_balance(id1,id2)
    args={'balance':balance,'active_user':active_user,'receive_user':receive_user,'relationship12':relationship12,'relationship21':relationship21,'form':form,'non_group_transactions':non_group_transactions,'final_group':grp_balance}
    return HttpResponseRedirect('/users/friend/'+id1+'/'+id2+'/')

def settle_group(request,id,grp_id):
    active_user=CustomUser.objects.get(pk=id)
    group=Group.objects.get(pk=grp_id)
    friend_amt_dict=group_settling_function(id,grp_id)
    for friend,amount in friend_amt_dict.items():
        name1=active_user.username+"-Settling-"+friend.username+"- "+group.grp_name+" Expenses"
        if amount !=0:
            t=Transaction(active_id=active_user,amt_paid=-amount,group_or_no=True,group_num=group,settling_or_no=True,trans_name=name1)
            t.save()
            relationship12=Relationship.objects.filter(active_id=active_user).filter(receiver_id=friend)[0]
            a=Accounts(trans_id=t,relation_id=relationship12,amt_exchanged=-amount)
            a.save()
    return HttpResponseRedirect('../')



def TimeSeriesViews(request,id):
    Data = Transaction.objects.filter(active_id__id=id).values('date','trans_tag').annotate(Sum('amt_paid'))
    Dict = {}
    Work = 'Work'
    Personal = 'Personal'
    Other = 'Other'
    categories = []
    Dict = {}
    Dict[Work] = {}
    Dict[Other] = {}
    Dict[Personal] = {}
    work = []
    other = []
    personal = []

    for row in Data:
        dat = row['date'].date().strftime('%d/%m/%y')
        if dat not in categories:
            categories.append(dat)
        if dat not in Dict[Work]:
            Dict[Work][dat] = 0
        if dat not in Dict[Personal]:
            Dict[Personal][dat] = 0
        if dat not in Dict[Other]:
            Dict[Other][dat] = 0
        Dict[row['trans_tag']][dat]+=row['amt_paid__sum']

        for i in categories:
            work.append(Dict[Work][i])
            personal.append(Dict[Personal][i])
            other.append(Dict[Other][i])
    
    context = {
        'categories':json.dumps(categories),
        'work':json.dumps(work),
        'personal':json.dumps(personal),
        'other':json.dumps(other),
    }
    return render(request,"hichart1.html",context)


def piMe(request,id):
    Data = Transaction.objects.filter(active_id__id=id).values('trans_tag').annotate(Sum('amt_paid'))
    chart = {
        'chart': {'type': 'pie'},
        'title': {'text': 'Pie Chart of The Kind of Expenditure'},
        'series': [{
            'name': 'Sum of Expenses',
            'data': list(map(lambda row: {'name':row['trans_tag'] , 'y': row['amt_paid__sum']},Data))
        }]
    }
    return JsonResponse(chart)



def ListFriends(request,id):
    Data = Relationship.objects.filter(active_id__id = id)

    return render(request,"friends.html",{'Data':Data})

def PiFriends(request,id1,id2):
    Data = Accounts.objects.select_related('trans_id').filter(trans_id__group_or_no = False,relation_id__active_id__id = id1,relation_id__receiver_id__id = id2).annotate(Sum('amt_exchanged'))
    Data2 = Accounts.objects.select_related('trans_id').filter(trans_id__group_or_no = False,relation_id__active_id__id = id2,relation_id__receiver_id__id = id1).values(name = 'relation_id__active_id__username').annotate(Sum('amt_exchanged'))
    name1 = CustomUser.objects.get(id=id1).username
    name2 = CustomUser.objects.get(id=id2).username
    sum1 = 0
    sum2 = 0
    for i in Data:
        sum1 = i['amt_exchanged__sum']
    for i in Data2:
        name2 = i['name']
        sum2 = i['amt_exchanged__sum']
        context = {
            'name1':name1,'name2':name2,'sum1':sum1,'sum2':sum2
        }
    return render(request,'hichart3.html',context) 


def BarFriends(request,id):
    Data = Relationship.objects.filter(active_id__id = id).values('receiver_id')
    rec_id = []
    friend_username = []
    friend_cost = []
    for i in Data:
        rec_id.append(i['receiver_id'])

    for i in rec_id:
        friend_username.append(CustomUser.objects.filter(id = i).values('username')[0]['username'])
        friend_cost.append(friend_balance(id,i))

    context = {
        'categories':json.dumps(friend_username),
        'column':json.dumps(friend_cost)
    }
    return render(request,"hichart4.html",context)


    
def json_example_2(request):
    return render(request, 'hichart3.html')
def json_example(request):
    return render(request, 'hichart2.html')

import xlwt

def export_users_xls(request,id):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Date','Transaction No', 'Person 1', 'Person 2', 'Amount Exchanged']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()

    rows = Accounts.objects.select_related('trans_id','relation_id').filter(relation_id__active_id__id = id).values_list('trans_id__date','trans_id__id','relation_id__active_id__username','relation_id__receiver_id__username','amt_exchanged')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    
    rows = Accounts.objects.select_related('trans_id','relation_id').filter(relation_id__receiver_id__id = id).values_list('trans_id__date','trans_id__id','relation_id__active_id__username','relation_id__receiver_id__username','amt_exchanged')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response
