# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import OwnerProfile, PrintRequest
from .models import PrintCostConfig

class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)  # Adding confirm password field to ensure password match

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class OwnerRegistrationForm(forms.ModelForm):
    class Meta:
        model = OwnerProfile
        fields = ['shop_name', 'opening_time', 'closing_time', 'landmark' ]

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

class FileUploadForm(forms.ModelForm):
    PAGE_CHOICES = [
        ('all', 'All Pages'),
        ('range', 'Page Range'),
    ]
    
    page_choice = forms.ChoiceField(choices=PAGE_CHOICES, widget=forms.RadioSelect, initial='all', label="Pages to Print")
    start_page = forms.IntegerField(required=False, label="Start Page")
    end_page = forms.IntegerField(required=False, label="End Page")
    copies = forms.IntegerField(min_value=1, initial=1, label="Number of Copies")

    class Meta:
        model = PrintRequest
        exclude = ['student', 'shop','pages']  # Exclude 'pages' field, we'll set it in the view
        widgets = {
            'print_config': forms.Select(choices=[('Color', 'Color'), ('Black & White', 'Black & White')])
        }

    def clean(self):
        cleaned_data = super().clean()
        page_choice = cleaned_data.get("page_choice")
        start_page = cleaned_data.get("start_page")
        end_page = cleaned_data.get("end_page")

        if page_choice == 'range' and (start_page is None or end_page is None):
            raise forms.ValidationError("Specify both start and end pages for the page range.")
        elif page_choice == 'range' and start_page > end_page:
            raise forms.ValidationError("Start page must be less than or equal to end page.")
        return cleaned_data
    
    
    
class PrintCostForm(forms.ModelForm):
    class Meta:
        model = PrintCostConfig
        fields = ['color_print_cost', 'black_white_print_cost']

        # Optionally, you can add custom labels or help texts
        labels = {
            'color_print_cost': 'Cost per page (Color)',
            'black_white_print_cost': 'Cost per page (Black & White)',
        }
        help_texts = {
            'color_print_cost': 'Set the cost for color printing.',
            'black_white_print_cost': 'Set the cost for black and white printing.',
        }    