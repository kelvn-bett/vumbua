from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from .models import Profile, Comments, Ideas, Forum, ForumComments, Interest

GENDER_CHOICES = [
    ('MALE', 'Male'),
    ('FEMALE', 'Female'),
]
CAT_CHOICES = [
    ('IT', 'IT'),
    ('Human Resource', 'Human Resource'),
    ('Finance', 'Finance'),
    ('Health', 'Health'),
    ('Business', 'Business'),
    ('Agriculture', 'Agriculture'),
    ('Entertainment', 'Entertainment'),
]


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("This User does not exist")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect username or password")
            if not user.is_active:
                raise forms.ValidationError("This User  is not active")
        return super(UserLoginForm, self).clean()


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    category = forms.ChoiceField(choices=CAT_CHOICES)
    phone_number = forms.CharField(max_length=10)

    class Meta:
        model = User
        fields = ['username', 'email', 'gender', 'category', 'phone_number', 'password1', 'password2']

    # def clean_email(self):
    #     email = self.cleaned_data['email']
    #     # check if valid
    #     if validate_email(email) is False:
    #         raise forms.ValidationError("Provided email address is not valid")
    #     # check if unique
    #     q1 = User.objects.filter(email__iexact=email).count()
    #     if q1 >= 1:
    #         raise forms.ValidationError("Provided email address exists")
    #
    #     return email


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = "Profile Picture"


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['body']

    def __init__(self, *args, **kwargs):
        super(CommentsForm, self).__init__(*args, **kwargs)
        self.fields['body'].label = "Comment"


class IdeaCreationForm(forms.ModelForm):

    class Meta:
        model = Ideas
        exclude = ['status', 'date_posted', 'likes', 'dislikes', 'user', 'role','approved','denied','total','votes','voted_id']


class ForumCommentsForm(forms.ModelForm):
    class Meta:
        model = ForumComments
        fields = ['body']


class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum
        fields = ['title', 'body']
    # title = forms.CharField(max_length = 50)
    # problem_statement = forms.CharField(widget=forms.Textarea,max_length = 4000)
    # executive_summary = forms.CharField(widget=forms.Textarea,max_length = 4000)
    # objectives = forms.CharField(widget=forms.Textarea,max_length = 4000)
    # limitations = forms.CharField(widget=forms.Textarea,max_length = 4000)


class InterestForm(forms.ModelForm):
    class Meta:
        model = Interest
        fields = ['title', 'body']

    def __init__(self, *args, **kwargs):
        super(InterestForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = "Offer"
