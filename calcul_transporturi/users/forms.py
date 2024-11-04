from django import forms
from .models import CustomUser

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label='Parolă')
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'user_type']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        # Setează is_staff pe baza tipului de utilizator
        if self.cleaned_data['user_type'] == 'Staff':
            user.is_staff = True
        else:
            user.is_staff = False

        if commit:
            user.save()
        return user
