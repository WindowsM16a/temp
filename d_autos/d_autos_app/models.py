from decimal import Decimal
from datetime import date, timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

# =========================
# CUSTOMER MODEL
# =========================
class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True)

    # 🔐 Driver License Details
    license_number = models.CharField(max_length=50, unique=True)
    license_type = models.CharField(max_length=20, blank=True)  # e.g. Class B, C, D
    license_issue_date = models.DateField()
    license_expiry_date = models.DateField()

    # Additional Information
    date_of_birth = models.DateField(blank=True, null=True)
    national_id = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, help_text="Additional notes about the customer")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.license_number})"




# =========================
# CAR MODEL
# =========================
class Car(models.Model):
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ]

    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    plate_number = models.CharField(max_length=20, unique=True)
    rental_price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)
    color = models.CharField(max_length=30, default='White')
    mileage = models.IntegerField(default=0, help_text="Current mileage in kilometers")
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='petrol')
    notes = models.TextField(blank=True, help_text="Additional notes about the car")
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    license_plate = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, default='available')

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number})"
    
    
    def save(self, *args, **kwargs):
        # Set daily_rate from rental_price_per_day if not set
        if not self.daily_rate and self.rental_price_per_day:
            self.daily_rate = self.rental_price_per_day
        if not self.license_plate and self.plate_number:
            self.license_plate = self.plate_number
        if not self.status:
            self.status = 'available' if self.availability else 'unavailable'
        super().save(*args, **kwargs)

# =========================
# RENTAL MODEL  
# =========================

class Rental(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('returned', 'Returned'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partial'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    employee = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True)
    rental_date = models.DateField()
    return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    deposit_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    notes = models.TextField(blank=True, help_text="Additional notes about the rental")

    # Equipment fields
    equipment_gps = models.BooleanField(default=False)
    equipment_child_seat = models.BooleanField(default=False)
    equipment_roof_rack = models.BooleanField(default=False)
    equipment_premium_insurance = models.BooleanField(default=False)
    equipment_driver = models.BooleanField(default=False)
    equipment_wifi = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Only prevent creating a new active rental for an unavailable car.
        # Allow saving/updating existing rentals (e.g., marking paid or updating fields).
        if self.status == 'active' and not self.car.availability and getattr(self, '_state', None) and getattr(self._state, 'adding', False):
            raise ValueError("This car is already rented.")

        days = (self.return_date - self.rental_date).days
        if days < 1:
            days = 1

        # Calculate base cost
        base_cost = days * self.car.rental_price_per_day

        # Add equipment costs
        equipment_cost = 0
        if self.equipment_gps:
            equipment_cost += 10 * days
        if self.equipment_child_seat:
            equipment_cost += 5 * days
        if self.equipment_roof_rack:
            equipment_cost += 8 * days
        if self.equipment_premium_insurance:
            equipment_cost += 15 * days
        if self.equipment_driver:
            equipment_cost += 20 * days
        if self.equipment_wifi:
            equipment_cost += 12 * days

        self.total_cost = base_cost + equipment_cost

        self.car.availability = self.status != 'active'
        self.car.save()

        super().save(*args, **kwargs)

def __str__(self):
    return f"Rental {self.id} - {self.car} by {self.customer}"


# =========================
# PAYMENT MODEL
# =========================

class Payment(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Customer')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=date.today)
    payment_method = models.CharField(max_length=20)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    )
    payment_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Transaction Information
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Transaction ID',
        help_text='Reference number from payment processor'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Payment Notes',
        help_text='Additional notes about this payment'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Auto mark rental as paid without calling Rental.save()
        # (calling Rental.save() may re-check car availability and raise)
        if self.payment_status == 'paid' and self.rental_id:
            from django.db import connection
            # Use queryset .update() to avoid running Rental.save()
            Rental.objects.filter(pk=self.rental_id).update(payment_status='paid')

    def __str__(self):
        return f"Payment for Rental {self.rental.id}"
    
    



# =========================
# RESERVATION MODEL
# =========================
class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reservation_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Deposit amount required for this reservation"
    )
    special_requests = models.TextField(
        blank=True,
        help_text="Any special requirements or requests from the customer"
    )
    additional_equipment = models.CharField(
        max_length=200,
        blank=True,
        help_text="Additional equipment requested (GPS, child seat, etc.)"
    )

    def __str__(self):
        return f"{self.customer} reserved {self.car}"




# =========================
# ENHANCED MAINTENANCE MODEL
# =========================
class Maintenance(models.Model):
    # Status Choices
    STATUS_SCHEDULED = 'scheduled'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]
    
    # Priority Choices
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_CRITICAL = 'critical'
    
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_CRITICAL, 'Critical'),
    ]
    
    # Maintenance Type Choices (Common services)
    TYPE_OIL_CHANGE = 'oil_change'
    TYPE_TIRE_ROTATION = 'tire_rotation'
    TYPE_BRAKE_SERVICE = 'brake_service'
    TYPE_ENGINE_TUNE = 'engine_tune'
    TYPE_TRANSMISSION = 'transmission'
    TYPE_SUSPENSION = 'suspension'
    TYPE_ELECTRICAL = 'electrical'
    TYPE_AIR_CONDITIONING = 'air_conditioning'
    TYPE_GENERAL_SERVICE = 'general_service'
    TYPE_BODY_REPAIR = 'body_repair'
    TYPE_GLASS_REPLACEMENT = 'glass_replacement'
    TYPE_INTERIOR = 'interior'
    TYPE_EXTERIOR = 'exterior'
    
    MAINTENANCE_TYPE_CHOICES = [
        (TYPE_OIL_CHANGE, 'Oil Change'),
        (TYPE_TIRE_ROTATION, 'Tire Rotation'),
        (TYPE_BRAKE_SERVICE, 'Brake Service'),
        (TYPE_ENGINE_TUNE, 'Engine Tune-up'),
        (TYPE_TRANSMISSION, 'Transmission Service'),
        (TYPE_SUSPENSION, 'Suspension Repair'),
        (TYPE_ELECTRICAL, 'Electrical System'),
        (TYPE_AIR_CONDITIONING, 'Air Conditioning'),
        (TYPE_GENERAL_SERVICE, 'General Service'),
        (TYPE_BODY_REPAIR, 'Body Repair'),
        (TYPE_GLASS_REPLACEMENT, 'Glass Replacement'),
        (TYPE_INTERIOR, 'Interior Repair'),
        (TYPE_EXTERIOR, 'Exterior Repair'),
    ]
    
    # Foreign Keys
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='maintenances',
        verbose_name='Car'
    )
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenances',
        verbose_name='Assigned Mechanic',
        limit_choices_to={'role__in': ['mechanic', 'manager', 'technician']}  # Only mechanics can be assigned
    )
    
    # Dates
    scheduled_date = models.DateField(
        verbose_name='Scheduled Date',
        help_text='Date when maintenance is scheduled to start',
        default=date.today
    )
    completed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Completed Date',
        help_text='Date when maintenance was actually completed'
    )
    
    # Next service recommendation
    next_service_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Next Service Date',
        help_text='Recommended date for next service'
    )
    next_service_mileage = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Next Service Mileage',
        help_text='Recommended mileage for next service'
    )
    
    # Basic Information
    service_type = models.CharField(
        max_length=50,
        choices=MAINTENANCE_TYPE_CHOICES,
        verbose_name='Maintenance Type',
        help_text='Type of maintenance/service performed',
        default=TYPE_GENERAL_SERVICE
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Maintenance Title',
        help_text='Short description of the maintenance',
        default='General Maintenance Service'
    )
    
    # Status & Priority
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SCHEDULED,
        verbose_name='Status',
        help_text='Current status of the maintenance'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        verbose_name='Priority',
        help_text='Priority level of the maintenance'
    )
    
    # Cost Information
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Total Cost',
        help_text='Total cost of maintenance in Ghana Cedis (₵)',
        default=0.00
    )
    labor_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Labor Cost',
        help_text='Cost of labor only',
        default=0.00
    )
    parts_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Parts Cost',
        help_text='Cost of parts/materials only',
        default=0.00
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Tax Amount',
        help_text='Tax amount included in total',
        default=0.00
    )
    
    # Parts & Materials
    parts_used = models.TextField(
        blank=True,
        verbose_name='Parts Used',
        help_text='List of parts and materials used (comma-separated or one per line)',
        default=''
    )
    parts_quantity = models.TextField(
        blank=True,
        verbose_name='Parts Quantity',
        help_text='Quantity of each part used',
        default=''
    )
    
    # Description & Documentation
    description = models.TextField(
        verbose_name='Detailed Description',
        help_text='Detailed description of the maintenance work performed',
        default='Standard maintenance service performed.'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Additional Notes',
        help_text='Any additional notes, recommendations, or special instructions',
        default=''
    )
    
    # Mileage Information
    mileage_at_service = models.IntegerField(
        verbose_name='Mileage at Service',
        help_text='Car mileage when maintenance was performed (in km)',
        default=0
    )
    
    # Warranty Information
    warranty_period = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Warranty Period (days)',
        help_text='Warranty period for this service in days',
        default=30
    )
    warranty_expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Warranty Expiry Date',
        help_text='Date when warranty for this service expires'
    )
    
    # Approval & Authorization
    approved_by = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_maintenances',
        verbose_name='Approved By',
        limit_choices_to={'role__in': ['manager', 'supervisor']}
    )
    approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Approval Date'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # File attachments (if needed for later implementation)
    # invoice_file = models.FileField(upload_to='maintenance_invoices/', null=True, blank=True)
    # report_file = models.FileField(upload_to='maintenance_reports/', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Maintenance Record'
        verbose_name_plural = 'Maintenance Records'
        ordering = ['-scheduled_date', 'priority']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['car', 'scheduled_date']),
            models.Index(fields=['employee', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.car.brand} {self.car.model} ({self.scheduled_date})"
    
    # Custom Properties/Methods
    
    @property
    def duration_days(self):
        """Calculate duration in days if completed"""
        if self.completed_date and self.scheduled_date:
            return (self.completed_date - self.scheduled_date).days
        return None
    
    @property
    def is_overdue(self):
        """Check if scheduled maintenance is overdue"""
        if self.status == self.STATUS_SCHEDULED and self.scheduled_date < date.today():
            return True
        return False
    
    @property
    def is_warranty_valid(self):
        """Check if warranty is still valid"""
        if self.warranty_expiry_date:
            return self.warranty_expiry_date >= date.today()
        return False
    
    @property
    def days_since_completion(self):
        """Calculate days since completion"""
        if self.completed_date:
            return (date.today() - self.completed_date).days
        return None
    
    @property
    def status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            self.STATUS_SCHEDULED: 'status-badge active',
            self.STATUS_IN_PROGRESS: 'status-badge warning',
            self.STATUS_COMPLETED: 'status-badge success',
            self.STATUS_CANCELLED: 'status-badge danger',
        }
        return status_classes.get(self.status, 'status-badge')
    
    @property
    def priority_badge_class(self):
        """Return CSS class for priority badge"""
        priority_classes = {
            self.PRIORITY_LOW: 'priority-badge low',
            self.PRIORITY_MEDIUM: 'priority-badge medium',
            self.PRIORITY_HIGH: 'priority-badge high',
            self.PRIORITY_CRITICAL: 'priority-badge critical',
        }
        return priority_classes.get(self.priority, 'priority-badge')
    
    def save(self, *args, **kwargs):
        # Auto-calculate next service if not set
        if not self.next_service_date and self.completed_date:
            # Add 6 months for most services, 1 year for major services
            if self.service_type in [self.TYPE_OIL_CHANGE, self.TYPE_TIRE_ROTATION, self.TYPE_GENERAL_SERVICE]:
                self.next_service_date = self.completed_date + timedelta(days=180)  # 6 months
                if self.mileage_at_service:
                    self.next_service_mileage = self.mileage_at_service + 5000
            else:
                self.next_service_date = self.completed_date + timedelta(days=365)  # 1 year
                if self.mileage_at_service:
                    self.next_service_mileage = self.mileage_at_service + 10000
        
        # Auto-calculate warranty expiry if warranty period is set
        if self.warranty_period and self.completed_date and not self.warranty_expiry_date:
            self.warranty_expiry_date = self.completed_date + timedelta(days=self.warranty_period)
        
        # Auto-calculate cost breakdown if not provided
        if self.cost and not (self.labor_cost or self.parts_cost):
            # Default breakdown: 60% labor, 35% parts, 5% tax
            self.labor_cost = self.cost * Decimal('0.6')
            self.parts_cost = self.cost * Decimal('0.35')
            self.tax_amount = self.cost * Decimal('0.05')
        
        # Auto-update car last service date when maintenance is completed
        if self.status == self.STATUS_COMPLETED and self.completed_date:
            self.car.last_service_date = self.completed_date
            self.car.save(update_fields=['last_service_date'])
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('maintenance_detail', kwargs={'pk': self.pk})



# =========================
# CUSTOM USER MODEL
# =========================

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    """Custom User model with email as username and user type."""
    
    # User Types
    USER_TYPE_ADMIN = 'admin'
    USER_TYPE_EMPLOYEE = 'employee'
    USER_TYPE_CHOICES = [
        (USER_TYPE_ADMIN, 'Administrator'),
        (USER_TYPE_EMPLOYEE, 'Employee'),
    ]
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default=USER_TYPE_EMPLOYEE,
        verbose_name='User Type'
    )
    phone = models.CharField(max_length=15, blank=True, verbose_name='Phone Number')
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        verbose_name='Profile Image'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"

    @property
    def is_admin(self):
        return self.user_type == self.USER_TYPE_ADMIN or self.is_superuser

    @property
    def is_employee(self):
        return self.user_type == self.USER_TYPE_EMPLOYEE

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

class Employee(models.Model):
    """Employee profile linked to User."""
    
    # Employee Roles
    ROLE_MANAGER = 'manager'
    ROLE_SALES_AGENT = 'sales_agent'
    ROLE_MECHANIC = 'mechanic'
    ROLE_ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (ROLE_MANAGER, 'Manager'),
        (ROLE_SALES_AGENT, 'Sales Agent'),
        (ROLE_MECHANIC, 'Mechanic'),
        (ROLE_ADMIN, 'Administrator'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        verbose_name='User Account'
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Employee ID'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='Role'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Department'
    )
    hire_date = models.DateField(verbose_name='Hire Date')
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Salary'
    )
    address = models.TextField(blank=True, verbose_name='Address')
    emergency_contact = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Emergency Contact'
    )
    emergency_phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Emergency Phone'
    )
    
    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['employee_id']
    
    def __str__(self):
        return f"{self.user.full_name} ({self.employee_id})"
    
    @property
    def phone(self):
        """Return the employee's phone number from the User model"""
        return self.user.phone
    
    def save(self, *args, **kwargs):
        if not self.employee_id:
            # Generate employee ID
            last_employee = Employee.objects.order_by('id').last()
            if last_employee:
                last_id = int(last_employee.employee_id.split('-')[1])
                new_id = f"EMP-{last_id + 1:04d}"
            else:
                new_id = "EMP-0001"
            self.employee_id = new_id
        super().save(*args, **kwargs)