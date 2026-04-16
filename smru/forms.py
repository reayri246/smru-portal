from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Complaint, StudentProfile, UserRole, ComplaintCategory, ComplaintPerson, College


def get_college_choices():
    college_choices = [(college.pk, str(college.name)) for college in College.objects.all()]
    college_choices.append(('other', 'Other'))
    return [('', 'Select College')] + college_choices


class SignUpForm(UserCreationForm):
    ROLE_CHOICES = (
        ('', 'Select Role'),
        ('student', 'Student'),
        ('hod', 'Head of Department'),
        ('chairman', 'Chairman'),
        ('principal', 'Principal'),
        ('director', 'Director'),
        ('faculty', 'Faculty'),
        ('security', 'Security'),
        ('anti_ragging_team', 'Anti Ragging Team'),
        ('she_team', 'SHE Team'),
        ('other', 'Other'),
    )
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_role',
            'onchange': 'toggleStudentFields()'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number',
            'id': 'id_phone'
        })
    )
    
    # Student specific fields
    student_college_type = forms.ChoiceField(
        choices=[
            ('', 'Select College Type'),
            ('engineering', 'Engineering College'),
            ('medical', 'Medical College'),
            ('other', 'Other College'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_college_type',
            'onchange': 'updateCollegeList()'
        }),
        label='College Type'
    )
    
    college = forms.ChoiceField(
        choices=get_college_choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_college'
        }),
        label='College Name',
    )
    
    other_college_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your college name',
            'id': 'id_other_college_name'
        }),
        label='Other College Name'
    )
    
    branch = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Branch',
            'id': 'id_branch'
        })
    )
    
    year = forms.ChoiceField(
        choices=[
            ('', 'Select Year'),
            ('1', '1st Year'),
            ('2', '2nd Year'),
            ('3', '3rd Year'),
            ('4', '4th Year'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_year'
        })
    )
    
    hall_ticket_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Hall Ticket Number',
            'id': 'id_hall_ticket'
        })
    )
    
    id_card = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'id_id_card',
            'capture': 'environment'
        }),
        label='Student ID Card Photo'
    )
    
    pan_card = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'id_pan_card',
            'capture': 'environment'
        }),
        label='PAN Card Photo'
    )
    
    live_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'id_live_photo',
            'capture': 'user'
        }),
        label='Live Selfie for Verification'
    )

    
    # Non-student department field
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Department (for HOD, Faculty, etc.)',
            'id': 'id_department',
            'style': 'display:none;'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            # Check minimum length
            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
            
            # Check for at least one uppercase letter
            if not any(char.isupper() for char in password):
                raise forms.ValidationError("Password must contain at least one uppercase letter.")
            
            # Check for at least one lowercase letter
            if not any(char.islower() for char in password):
                raise forms.ValidationError("Password must contain at least one lowercase letter.")
            
            # Check for at least one digit
            if not any(char.isdigit() for char in password):
                raise forms.ValidationError("Password must contain at least one number.")
            
            # Check for at least one special character
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(char in special_chars for char in password):
                raise forms.ValidationError("Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?).")
            
            # Check that password is not entirely numeric
            if password.isdigit():
                raise forms.ValidationError("Password cannot be entirely numeric.")
            
            # Check that password is not too similar to username
            username = self.cleaned_data.get('username', '')
            if username and password.lower() in username.lower() or username.lower() in password.lower():
                raise forms.ValidationError("Password cannot be too similar to your username.")
        
        return password

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        if role == 'student':
            # All student fields are mandatory
            student_fields = {
                'student_college_type': 'College Type',
                'college': 'College Name',
                'branch': 'Branch',
                'year': 'Year',
                'hall_ticket_number': 'Hall Ticket Number',
                'phone': 'Phone Number',
                'live_photo': 'Live Selfie',
            }
            
            for field, label in student_fields.items():
                if not cleaned_data.get(field):
                    raise forms.ValidationError(f"{label} is required for students.")
            
            # Either Student ID or PAN card must be provided (choose one)
            if not cleaned_data.get('id_card') and not cleaned_data.get('pan_card'):
                raise forms.ValidationError("Either Student ID Card or PAN Card must be uploaded. Choose one.")
            
            # If "Other" college is selected, other_college_name is required
            college_value = cleaned_data.get('college')
            if college_value == 'other':
                if not cleaned_data.get('other_college_name'):
                    raise forms.ValidationError("Please specify the name of your college when selecting 'Other'.")
            elif college_value:
                # Convert college choice back to College object for processing
                try:
                    cleaned_data['college'] = College.objects.get(pk=college_value)
                except College.DoesNotExist:
                    raise forms.ValidationError("Invalid college selection.")
        
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class ForgotPasswordForm(forms.Form):
    CONTACT_CHOICES = (
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
    )
    
    username_or_email = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Username or Email Address',
            'autofocus': True
        }),
        label='Username or Email'
    )
    
    reset_method = forms.ChoiceField(
        choices=CONTACT_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='How should we send the reset link?'
    )


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        }),
        label='New Password'
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }),
        label='Confirm Password'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password')
        password2 = cleaned_data.get('confirm_password')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")
            if len(password1) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
        
        return cleaned_data


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['category', 'person', 'complaint_text', 'file', 'feedback']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'person': forms.Select(attrs={
                'class': 'form-control'
            }),
            'complaint_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your complaint...',
                'rows': 5
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.png,.zip'
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Optional feedback...',
                'rows': 3
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user and hasattr(self.user, 'student_profile') and self.user.student_profile:
            # For students from listed colleges
            if self.user.student_profile.is_from_listed_college:
                self.fields['category'].queryset = ComplaintCategory.objects.filter(type='listed_college', is_active=True)
            else:
                # For students from other colleges
                self.fields['category'].queryset = ComplaintCategory.objects.filter(type='other_college', is_active=True)
        else:
            # For non-students
            self.fields['category'].queryset = ComplaintCategory.objects.filter(type='other_college', is_active=True)
        
        # Filter persons based on selected category
        if self.instance and hasattr(self.instance, 'category') and self.instance.category:
            self.fields['person'].queryset = ComplaintPerson.objects.filter(category=self.instance.category, is_active=True)
        else:
            self.fields['person'].queryset = ComplaintPerson.objects.none()


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['roll_number', 'phone', 'bio', 'profile_picture']
        widgets = {
            'roll_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Roll Number'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about yourself...',
                'rows': 3
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

