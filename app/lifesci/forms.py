from django import forms
from django.utils.text import slugify
from crispy_forms.helper import FormHelper

from .models import Human, PreloadedUser, PeerReview


class HumanForm(forms.ModelForm):
    
    class Meta:
        model = Human
        fields = ['user', 'first_name', 'last_name', 'student_id', 'anonymous_user']

    # Add help text for anonymous user
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['student_id'] = forms.IntegerField(label='Student ID', required=True, help_text="Enter your 9-digit student ID.", error_messages={
            'invalid': 'Please enter a valid number.',
        })
        self.fields['anonymous_user'].help_text = "Check this box if you want to be anonymous."

        # Set user field using request.user
        self.fields['user'].initial = self.user

        # Hide User field
        self.fields['user'].widget = forms.HiddenInput()
    
    def clean(self):
        cleaned_data = super().clean()
        student_id = cleaned_data.get('student_id')
        preloaded_user_ids = [x.user_id for x in PreloadedUser.objects.all()]
        existing_user_ids = [x.student_id for x in Human.objects.all()]
        print(preloaded_user_ids, student_id)

        if student_id not in preloaded_user_ids:
            raise forms.ValidationError("Invalid student ID. Please try again.")
        
        print(student_id, existing_user_ids)
        if student_id in existing_user_ids:
            raise forms.ValidationError("This student ID has already been used.")
        



    def save(self, commit=True):
        instance = super().save(commit=False)
        slug_base = slugify(f"{self.user.first_name}-{self.user.last_name}")
        unique_slug = slug_base[:20]  # Limit slug to 20 characters
        num = 1

        while Human.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug_base[:17]}-{num}"  # Limit slug to 17 characters and append num
            num += 1

        instance.slug = unique_slug
        #instance.user = self.initial['user']

        if commit:
            instance.save()
        return instance

class IntegerInputForm(forms.Form):
    number = forms.IntegerField(label='Answer')
    figure = forms.FileField(label='Figure')

class PeerReviewForm(forms.ModelForm):

    class Meta:
        model = PeerReview
        fields = ['human', 'answer', 'feedback', 'pass_peer']

    # Add help text for anonymous user
    def __init__(self, *args, **kwargs):
        self.answer = kwargs.pop('answer', None)
        self.human = kwargs.pop('human', None)
        super().__init__(*args, **kwargs)

        self.fields['human'].initial = self.human
        self.fields['answer'].initial = self.answer

        self.fields['human'].widget = forms.HiddenInput()
        self.fields['answer'].widget = forms.HiddenInput()
        self.fields['pass_peer'].label = "Pass peer review"

class FigureOnlyForm(forms.Form):
    resubmit_figure = forms.FileField(label='Resubmit figure')

        




    

