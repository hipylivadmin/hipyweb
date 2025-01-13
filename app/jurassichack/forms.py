from django import forms

from .models import Character

class StartForm(forms.Form):
    character_name = forms.CharField(label='Character Name')

class InputForm(forms.Form):
    input = forms.IntegerField(label='Console Input')

