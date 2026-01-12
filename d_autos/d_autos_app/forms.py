from django import forms
from .models import (
    Customer, Car, Rental,
    Payment, Reservation, Maintenance, Employee
)
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User
import random


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'phone',
            'email',
            'address',
            'license_number',
            'license_type',
            'license_issue_date',
            'license_expiry_date',
            'date_of_birth',
            'national_id',
            'notes',
        ]

        widgets = {
            'license_issue_date': forms.DateInput(attrs={'type': 'date'}),
            'license_expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter full address including street, city, and postal code'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Add any special notes about this customer (preferences, restrictions, etc.)'
            }),
        }


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['brand', 'model', 'year', 'plate_number', 'rental_price_per_day', 
                  'color', 'mileage', 'fuel_type', 'availability', 'notes']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Toyota, BMW, Mercedes'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Camry, 3 Series'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'min': '1990', 'max': str(__import__('datetime').datetime.now().year + 1)}),
            'plate_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., GA-XXX-XX'}),
            'rental_price_per_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Red, Blue, Black'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'min': '0', 'placeholder': 'Current mileage in km'}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'availability': forms.CheckboxInput(attrs={'class': 'checkbox-input'}),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Add any special features or requirements for this car'
            }),
        }


class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = '__all__'
        widgets = {
            'rental_date': forms.DateInput(attrs={'type': 'date'}),
            'return_date': forms.DateInput(attrs={'type': 'date'}),
            'actual_return_date': forms.DateInput(attrs={'type': 'date'}),
            'total_cost': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'deposit_paid': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add any special notes about this rental'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ONLY AVAILABLE CARS
        self.fields['car'].queryset = Car.objects.filter(availability=True)
        # Format car choices with prices
        car_choices = []
        for car in Car.objects.filter(availability=True):
            price = car.rental_price_per_day or car.daily_rate or 0
            car_choices.append((
                car.id,
                f"{car.brand} {car.model} ({car.plate_number}) - ₵{price}"
            ))
        self.fields['car'].choices = car_choices
        # Make employee optional on the form (we assign it in the view)
        if 'employee' in self.fields:
            self.fields['employee'].required = False

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'transaction_id': forms.TextInput(attrs={
                'placeholder': 'Enter transaction reference number'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add any special notes about this payment'
            }),
        }


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'deposit_amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'special_requests': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Any special requirements or requests from the customer'
            }),
            'additional_equipment': forms.TextInput(attrs={
                'placeholder': 'GPS, child seat, etc.'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add data attributes to car choices with rental prices
        car_choices = []
        for car in Car.objects.filter(availability=True):
            price = car.rental_price_per_day or car.daily_rate or 0
            car_choices.append((
                car.id,
                f"{car.brand} {car.model} ({car.plate_number}) - ₵{price}"
            ))
        self.fields['car'].choices = car_choices


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = '__all__'
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'completed_date': forms.DateInput(attrs={'type': 'date'}),
            'next_service_date': forms.DateInput(attrs={'type': 'date'}),
            'approval_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'parts_used': forms.Textarea(attrs={'rows': 3, 'placeholder': 'One part per line or comma-separated'}),
            'parts_quantity': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Corresponding quantities'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit employee choices to mechanics, managers, technicians
        self.fields['employee'].queryset = Employee.objects.filter(
            role__in=['mechanic', 'manager', 'technician']
        )
        # Limit approved_by choices to managers and supervisors
        self.fields['approved_by'].queryset = Employee.objects.filter(
            role__in=['manager', 'supervisor']
        )


class EmployeeForm(forms.ModelForm):
    # Additional User fields
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = Employee
        fields = ['role', 'department', 'hire_date', 'salary', 'address', 'emergency_contact', 'emergency_phone']
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter full address including street, city, and postal code'
            }),
            'role': forms.Select(attrs={'class': 'role-select'}),
            'department': forms.TextInput(attrs={
                'placeholder': 'e.g. Sales, Service, Management'
            }),
            'salary': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter monthly salary'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'placeholder': 'Name of emergency contact person'
            }),
            'emergency_phone': forms.TextInput(attrs={
                'placeholder': 'Emergency contact phone number'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user:
            # Populate User fields when editing
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone'].initial = self.instance.user.phone

    def save(self, commit=True):
        employee = super().save(commit=False)

        # Handle User creation/update
        if self.instance and self.instance.pk and self.instance.user:
            # Update existing user
            user = self.instance.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.phone = self.cleaned_data.get('phone', '')
            user.save()
        else:
            # Generate password: first 3 letters of first_name (uppercase) + 3 unique random numbers
            first_name = self.cleaned_data['first_name'].upper()
            name_part = first_name[:3] if len(first_name) >= 3 else first_name.ljust(3, 'X')
            
            # Generate 3 unique random digits
            digits = random.sample(range(10), 3)
            number_part = ''.join(map(str, digits))
            
            generated_password = name_part + number_part
            
            # Create new user with generated password
            user = User.objects.create_user(
                email=self.cleaned_data['email'],
                password=generated_password,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                phone=self.cleaned_data.get('phone', ''),
                user_type='employee'
            )
            employee.user = user
            
            # Store the generated password for display
            self.generated_password = generated_password

        if commit:
            employee.save()
        return employee


    # Custom Login Form
    
class UserLoginForm(AuthenticationForm):
    """Custom login form with user type selection."""
    
    USER_TYPE_CHOICES = [
        ('admin', 'Administrator'),
        ('employee', 'Employee'),
    ]
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'user-type-select'}),
        label='Login as',
        required=True
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'autocomplete': 'email'
        }),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email Address'
    
    def confirm_login_allowed(self, user):
        """Check if user can login based on user_type."""
        if not user.is_active:
            raise forms.ValidationError(
                _("This account is inactive."),
                code='inactive',
            )
        
        # Get selected user type from form data
        user_type = self.cleaned_data.get('user_type')
        
        if user_type == 'admin' and not user.is_admin:
            raise forms.ValidationError(
                _("You are not authorized to login as an administrator."),
                code='invalid_user_type',
            )
        
        if user_type == 'employee' and user.user_type != 'employee':
            raise forms.ValidationError(
                _("You are not authorized to login as an employee."),
                code='invalid_user_type',
            )
        
        return super().confirm_login_allowed(user)