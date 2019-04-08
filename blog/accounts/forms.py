from django import forms
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)

User = get_user_model()

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("This user does not exists")

            if not user.check_password(password):
                raise forms.ValidationError("Incorrect password")

            if not user.is_active:
                raise forms.ValidationError("This user is not longer active.")
        return super(UserLoginForm, self).clean(*args, **kwargs)

class UserRegistrationForm(forms.ModelForm):
    email= forms.EmailField(label='Email address')
    email_confirm = forms.EmailField(label='Confirm email')
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'email',
            'email_confirm'
        ]

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        email_confirm = self.cleaned_data.get('email_confirm')
        if email != email_confirm:
            raise forms.ValidationError("Emails must match")
        
        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
                raise forms.ValidationError("This email has already been registered")
        return super(UserRegistrationForm, self).clean(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_confirm = self.cleaned_data.get('email_confirm')
        if email != email_confirm:
            raise forms.ValidationError("Emails must match")
        
        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
                raise forms.ValidationError("This email has already been registered")

        return email