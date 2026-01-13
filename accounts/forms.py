from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, USER_ROLE_CHOICES


class CustomerUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=USER_ROLE_CHOICES, label='Роль')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=True)
        if commit:
            user.save()
            UserProfile.objects.create(user=user, role=self.cleaned_data['role'])
        return user


class ProfileUpdateForm(forms.ModelForm):

    first_name = forms.CharField(max_length=150, required=False, label='Имя')
    second_name = forms.CharField(max_length=150, required=False, label='Фамилия')
    email = forms.EmailField(required=False, label='Email')

    specialization = forms.CharField(max_length=255, required=False, label='Специализация', widget=forms.TextInput(attrs={'class': 'form-control'}))
    portfolio = forms.CharField(required=False, label='Портфолио', widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        self.profile_instance = kwargs.pop('profile_instance', None)
        super().__init__(*args, **kwargs)

        if self.profile_instance:
            self.fields['specialization'].initial = self.profile_instance.specialization
            self.fields['portfolio'].initial = self.profile_instance.portfolio

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

        if self.profile_instance:
            self.profile_instance.specialization = self.cleaned_data.get('specialization')
            self.profile_instance.portfolio = self.cleaned_data.get('portfolio')
            if commit:
                self.profile_instance.save()

        return user