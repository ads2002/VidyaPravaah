from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
from django import forms

from elearn.models import (Answer, Question, Learner, LearnerAnswer,
                              Course, User, Announcement, Parent)




class PostForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ('content', )

class ProfileForm(forms.ModelForm):
    email=forms.EmailField(widget=forms.EmailInput())
    confirm_email=forms.EmailField(widget=forms.EmailInput())

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',

        ]

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        email = cleaned_data.get("email")
        confirm_email = cleaned_data.get("confirm_email")

        if email != confirm_email:
            raise forms.ValidationError(
                "Emails must match!"
            )



class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email') 


class InstructorSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
            super(InstructorSignUpForm, self).__init__(*args, **kwargs)

            for fieldname in ['username', 'password1', 'password2']:
                self.fields[fieldname].help_text = None
                    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_instructor = True
        if commit:
            user.save()
        return user

class ParentSignUpForm(UserCreationForm):
    linked_learner = forms.ModelChoiceField(queryset=Learner.objects.all(),required=False,empty_label="Select Your Child")
    class Meta(UserCreationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
            super(ParentSignUpForm, self).__init__(*args, **kwargs)

            for fieldname in ['username', 'password1', 'password2']:
                self.fields[fieldname].help_text = None
                    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_parent = True
        if commit:
            user.save()
        return user
    # learner_name = forms.CharField(max_length=100, label="Enter Learner Name")

    # class Meta(UserCreationForm.Meta):
    #     model = User

    # def __init__(self, *args, **kwargs):
    #     super(ParentSignUpForm, self).__init__(*args, **kwargs)

    #     for fieldname in ['username', 'password1', 'password2']:
    #         self.fields[fieldname].help_text = None

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.is_parent = True
    #     if commit:
    #         user.save()
        
    #     learner_name = self.cleaned_data['learner_name']
        
    #     try:
    #         learner = Learner.objects.get(user__username=learner_name)
    #     except Learner.DoesNotExist:
    #         # Handle the case where the Learner with the given name does not exist
    #         # You can raise an error or handle it as needed
    #         return user

    #     parent = Parent(user=user, is_parent=True, learner_linked=learner)
    #     parent.save()
    #     connection = LearnerParentConnection(parent=parent, learner=learner)
    #     connection.save()

    #     return user
    # @transaction.atomic
    # def save(self):
    #     user = super().save(commit=False)
    #     user.is_parent = True
    #     user.save()
    #     learner = Parent.objects.create(user=user)
    #     learner.interests.add(*self.cleaned_data.get('learners'))
    #     return user

# class ParentUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Parent
#         fields = ('username', 'password1', 'password2','learner_linked')

class LearnerSignUpForm(UserCreationForm):
    interests = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User


    def __init__(self, *args, **kwargs):
            super(LearnerSignUpForm, self).__init__(*args, **kwargs)

            for fieldname in ['username', 'password1', 'password2']:
                self.fields[fieldname].help_text = None    

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_learner = True
        user.save()
        learner = Learner.objects.create(user=user)
        learner.interests.add(*self.cleaned_data.get('interests'))
        return user



class LearnerInterestsForm(forms.ModelForm):
    class Meta:
        model = Learner
        fields = ('interests', )
        widgets = {
            'interests': forms.CheckboxSelectMultiple
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', )


class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        has_one_correct_answer = False
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_correct', False):
                    has_one_correct_answer = True
                    break
        if not has_one_correct_answer:
            raise ValidationError('Mark at least one answer as correct.', code='no_correct_answer')


class TakeQuizForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=forms.RadioSelect(),
        required=True,
        empty_label=None)

    class Meta:
        model = LearnerAnswer
        fields = ('answer', )

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.order_by('text')


class LearnerCourse(forms.ModelForm):
    class Meta:
        model = Learner
        fields = ('interests', )
        widgets = {
            'interests': forms.CheckboxSelectMultiple
        }

    @transaction.atomic
    def save(self):
        learner = Learner()
        learner.interests.add(*self.cleaned_data.get('interests'))
        return learner_id
