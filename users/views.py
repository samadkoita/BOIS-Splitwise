from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

def my_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    return render(request,'login.html')
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect("/home/")
    else:
        # Return an 'invalid login' error message.
        ...

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    # Redirect to a success page.