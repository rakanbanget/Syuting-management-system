from __future__ import annotations
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, ShootingSchedule


COMMON_INPUT_CLASSES = 'w-full border rounded p-2'


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(required=True, label='Nama Depan')
    last_name = forms.CharField(required=True, label='Nama Belakang')
    phone = forms.CharField(required=False, label='No. Telepon')
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, label='Peran')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'phone', 'role',
            'password1', 'password2'
        )
        labels = {
            'username': 'Username',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{css} {COMMON_INPUT_CLASSES}".strip()

    def save(self, commit: bool = True) -> User:
        user: User = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data.get('phone', '')
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{css} {COMMON_INPUT_CLASSES}".strip()


class ShootingScheduleForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Tanggal')
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label='Waktu')

    class Meta:
        model = ShootingSchedule
        fields = ['title', 'date', 'time', 'location', 'description', 'script']
        labels = {
            'title': 'Judul/Scene',
            'location': 'Lokasi',
            'description': 'Deskripsi',
            'script': 'Script/Naskah',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{css} {COMMON_INPUT_CLASSES}".strip()
