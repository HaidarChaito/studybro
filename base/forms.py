from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User
from django import forms


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'members']


class UserForm(UserCreationForm):
    password1 = forms.CharField(
        label="New Password", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(
        label="Re-Enter Password", widget=forms.PasswordInput, required=False)
    avatar = forms.FileField(widget=forms.FileInput(
        attrs={"class": "form__group", "id": "avatar", "accept": "image/png, image/gif, image/jpeg"}))

    class Meta:
        model = User
        fields = ['avatar', 'username', 'password1', 'password2', 'about']
