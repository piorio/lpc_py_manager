from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    email = forms.EmailField(max_length=200, widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg'}))

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control form-control-lg'
        self.fields['password2'].widget.attrs['class'] = 'form-control form-control-lg'

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)
