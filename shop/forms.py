from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from .models import Profile, Comment

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'birth_date']



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Напишите ваш комментарий...',
                'class': 'form-control'
            })
        }
        labels = {'text': ''}


