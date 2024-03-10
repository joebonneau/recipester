from django import forms
from django.contrib.auth.forms import UserCreationForm

from recipester.models import User


class RecipeForm(forms.Form):
    name = forms.CharField()

    def clean_name(self):
        name = self.cleaned_data["name"]
        if name.lower() == "spam":
            raise forms.ValidationError("No spam allowed!")
        return name

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
