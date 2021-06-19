from django import forms
from .models import UserInfoModel

class UserSignupForm(forms.ModelForm):
    class Meta():
        model = UserInfoModel
        fields = '__all__'
