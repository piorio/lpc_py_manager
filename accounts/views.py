from django.shortcuts import render
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.shortcuts import render, redirect


# Create your views here.
#class SignUpView(generic.CreateView):
#    form_class = UserCreationForm
#    success_url = reverse_lazy('login')
#    template_name = 'registration/signup.html'

def signup_view(request):
    form = SignUpForm(request.POST)
    if form.is_valid():
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})