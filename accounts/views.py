from django.contrib import messages
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.shortcuts import render, redirect


# Create your views here.
def signup_view(request):
    form = SignUpForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
        else:
            for t in form.errors.values():
                messages.error(request, t.as_text())
            form = SignUpForm()
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
