from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, Car, Rental, Payment, Reservation, Maintenance, Employee, User
from .forms import CustomerForm, CarForm, EmployeeForm, RentalForm, PaymentForm, ReservationForm, MaintenanceForm
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import View
from .forms import UserLoginForm
from datetime import date
import random
from datetime import date
from decimal import Decimal

def is_admin(user):
    return user.is_authenticated and user.is_admin

def is_employee(user):
    return user.is_authenticated and user.is_employee

# ================= DASHBOARD VIEWS =================
@login_required
def dashboard(request):
    """Main dashboard that redirects based on user type."""
    if request.user.is_admin:
        return admin_dashboard_view(request)
    elif request.user.is_employee:
        return employee_dashboard_view(request)
    else:
        # Fallback to admin dashboard
        return admin_dashboard_view(request)

@login_required
@user_passes_test(is_admin, login_url='employee_dashboard')
def admin_dashboard_view(request):
    """Admin dashboard view."""
    # Summary counts
    total_customers = Customer.objects.count()
    total_cars = Car.objects.count()
    total_rentals = Rental.objects.count()
    
    # Calculate total revenue
    revenue_result = Payment.objects.aggregate(total=Sum('amount'))
    total_revenue = revenue_result['total'] or Decimal('0.00')

    # Rentals per Car
    rentals_per_car = (
        Rental.objects
        .values('car__brand', 'car__model')
        .annotate(total=Count('id'))
    )

    car_labels = [
        f"{r['car__brand']} {r['car__model']}"
        for r in rentals_per_car
    ]
    car_data = [r['total'] for r in rentals_per_car]

    # Revenue per Month
    revenue_per_month = (
        Payment.objects
        .annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    month_labels = [
        r['month'].strftime('%b %Y')
        for r in revenue_per_month
    ]
    month_data = [float(r['total'] or 0) for r in revenue_per_month]

    # Recent items for tables (limit to 5)
    recent_customers = Customer.objects.all().order_by('-id')[:5]
    recent_cars = Car.objects.all().order_by('-id')[:5]
    recent_rentals = Rental.objects.select_related('customer', 'car').all().order_by('-rental_date')[:5]

    # All data for tables
    all_customers = Customer.objects.all()
    all_cars = Car.objects.all()
    all_rentals = Rental.objects.select_related('customer', 'car', 'employee').order_by('-rental_date')
    all_payments = Payment.objects.select_related('rental', 'customer').order_by('-payment_date')
    all_maintenances = Maintenance.objects.select_related('car', 'employee').order_by('-scheduled_date')
    all_reservations = Reservation.objects.select_related('customer', 'car').order_by('-start_date')
    all_employees = Employee.objects.select_related('user').all()

    context = {
        'total_customers': total_customers,
        'total_cars': total_cars,
        'total_rentals': total_rentals,
        'total_revenue': total_revenue,

        'car_labels': car_labels,
        'car_data': car_data,
        'month_labels': month_labels,
        'month_data': month_data,
        'customers': recent_customers,
        'cars': recent_cars,
        'rentals': recent_rentals,
        'all_customers': all_customers,
        'all_cars': all_cars,
        'all_rentals': all_rentals,
        'all_payments': all_payments,
        'all_maintenances': all_maintenances,
        'all_reservations': all_reservations,
        'all_employees': all_employees,
    }

    return render(request, 'd_autos_app/dashboard.html', context)

@login_required
@user_passes_test(is_employee, login_url='admin_dashboard')
def employee_dashboard_view(request):
    """Employee dashboard view."""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        employee = None
    
    # Summary counts
    total_customers = Customer.objects.count()
    total_cars = Car.objects.count()
    total_rentals = Rental.objects.count()

    # Rentals handled by this employee
    employee_rentals = []
    employee_maintenances = []
    
    if employee:
        employee_rentals = Rental.objects.filter(employee=employee).select_related('customer', 'car').order_by('-rental_date')
        employee_maintenances = Maintenance.objects.filter(employee=employee).select_related('car').order_by('-scheduled_date')

    # Recent items (limit to 5)
    recent_customers = Customer.objects.all().order_by('-id')[:5]
    recent_cars = Car.objects.filter(availability=True).order_by('-id')[:5]

    # All data for tables
    all_customers = Customer.objects.all()
    all_cars = Car.objects.all()
    all_rentals = Rental.objects.select_related('customer', 'car', 'employee').order_by('-rental_date')
    all_payments = Payment.objects.select_related('rental', 'customer').order_by('-payment_date')
    all_maintenances = Maintenance.objects.select_related('car', 'employee').order_by('-scheduled_date')
    all_reservations = Reservation.objects.select_related('customer', 'car').order_by('-start_date')

    context = {
        'total_customers': total_customers,
        'total_cars': total_cars,
        'total_rentals': total_rentals,
        'rentals': employee_rentals,
        'maintenances': employee_maintenances,
        'employee': employee,
        'customers': recent_customers,
        'cars': recent_cars,
        'all_customers': all_customers,
        'all_cars': all_cars,
        'all_rentals': all_rentals,
        'all_payments': all_payments,
        'all_maintenances': all_maintenances,
        'all_reservations': all_reservations,
    }

    return render(request, 'd_autos_app/employee_dashboard.html', context)

# ================= CUSTOMER CRUD =================
@login_required
def customer_list(request):
    query = request.GET.get('q')
    customers = Customer.objects.all()

    if query:
        customers = customers.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(license_number__icontains=query)
        )

    return render(request, 'd_autos_app/customer.html', {'customers': customers})

@login_required
def customer_create(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Customer added successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/customer_form.html', {'form': form})

@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        messages.success(request, 'Customer updated successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/customer_form.html', {'form': form})

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/customer_confirm_delete.html', {'customer': customer})

# ================= CAR CRUD =================
@login_required
def car_list(request):
    status = request.GET.get('status')
    cars = Car.objects.all()

    if status == 'available':
        cars = cars.filter(availability=True)
    elif status == 'unavailable':
        cars = cars.filter(availability=False)

    return render(request, 'd_autos_app/cars.html', {'cars': cars})

@login_required
@login_required
def car_create(request):
    form = CarForm(request.POST or None)
    if form.is_valid():
        car = form.save()
        messages.success(request, f'Car {car.brand} {car.model} ({car.plate_number}) added successfully!')
        return redirect('car_list')
    return render(request, 'd_autos_app/cars_form.html', {'form': form})

@login_required
def car_update(request, pk):
    car = get_object_or_404(Car, pk=pk)
    form = CarForm(request.POST or None, instance=car)
    if form.is_valid():
        updated_car = form.save()
        messages.success(request, f'Car {updated_car.brand} {updated_car.model} updated successfully!')
        return redirect('car_list')
    return render(request, 'd_autos_app/cars_form.html', {'form': form})

@login_required
def car_delete(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        car.delete()
        messages.success(request, 'Car deleted successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/cars_confirm_delete.html', {'car': car})

# ================= RENTAL CRUD =================
@login_required
def rental_list(request):
    query = request.GET.get('q')
    rentals = Rental.objects.select_related('customer', 'car', 'employee').all()

    if query:
        rentals = rentals.filter(
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query) |
            Q(car__brand__icontains=query) |
            Q(car__model__icontains=query)
        )

    return render(request, 'd_autos_app/rentals.html', {'rentals': rentals})

@login_required
def rental_create(request):
    form = RentalForm(request.POST or None)
    if form.is_valid():
        rental = form.save(commit=False)
        # Assign employee from logged-in user if available
        try:
            rental.employee = request.user.employee_profile
        except Exception:
            rental.employee = None
        rental.save()
        messages.success(request, 'Rental created successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/rental_form.html', {'form': form})

@login_required
def rental_update(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    form = RentalForm(request.POST or None, instance=rental)
    if form.is_valid():
        updated_rental = form.save(commit=False)
        # If no employee set, try to assign current user's employee profile
        if not updated_rental.employee:
            try:
                updated_rental.employee = request.user.employee_profile
            except Exception:
                updated_rental.employee = None
        updated_rental.save()
        messages.success(request, 'Rental updated successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/rental_form.html', {'form': form})

@login_required
def rental_delete(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    if request.method == 'POST':
        rental.delete()
        messages.success(request, 'Rental deleted successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/rental_confirm_delete.html', {'rental': rental})

@login_required
def return_rental(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    rental.status = 'returned'
    rental.car.availability = True
    rental.car.save()
    rental.save()
    messages.success(request, 'Rental returned successfully!')
    return redirect('dashboard')

# ================= PAYMENT CRUD =================
@login_required
def payment_list(request):
    payments = Payment.objects.select_related('rental', 'customer')
    return render(request, 'd_autos_app/payments.html', {'payments': payments})

@login_required
def payment_create(request):
    form = PaymentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Payment recorded successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/payment_form.html', {'form': form})

@login_required
def payment_update(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    form = PaymentForm(request.POST or None, instance=payment)
    if form.is_valid():
        form.save()
        messages.success(request, 'Payment updated successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/payment_form.html', {'form': form})

@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/payment_confirm_delete.html', {'payment': payment})

# ================= RESERVATION CRUD =================
@login_required
def reservation_list(request):
    reservations = Reservation.objects.select_related('customer', 'car')
    return render(request, 'd_autos_app/reservations.html', {'reservations': reservations})

@login_required
def reservation_create(request):
    form = ReservationForm(request.POST or None)
    context = {'form': form}
    if request.method == 'POST' and not form.is_valid():
        # try to calculate from data
        start_str = request.POST.get('start_date')
        end_str = request.POST.get('end_date')
        if start_str and end_str:
            try:
                start_date = date.fromisoformat(start_str)
                end_date = date.fromisoformat(end_str)
                duration_days = (end_date - start_date).days
                context['duration'] = f"{duration_days} days"
            except ValueError:
                context['duration'] = "0 days"
        else:
            context['duration'] = "0 days"
    else:
        context['duration'] = "0 days"
    if form.is_valid():
        form.save()
        messages.success(request, 'Reservation created successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/reservations_form.html', context)

@login_required
def reservation_update(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    form = ReservationForm(request.POST or None, instance=reservation)
    context = {'form': form}
    if reservation.start_date and reservation.end_date:
        duration_days = (reservation.end_date - reservation.start_date).days
        context['duration'] = f"{duration_days} days"
    else:
        context['duration'] = "0 days"
    if form.is_valid():
        form.save()
        messages.success(request, 'Reservation updated successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/reservations_form.html', context)

@login_required
def reservation_delete(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, 'Reservation deleted successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/reservations_confirm_delete.html', {'reservation': reservation})

# ================= MAINTENANCE CRUD =================
@login_required
def maintenance_list(request):
    maintenances = Maintenance.objects.select_related('car', 'employee')
    return render(request, 'd_autos_app/maintenances.html', {'maintenances': maintenances})

@login_required
def maintenance_create(request):
    form = MaintenanceForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Maintenance scheduled successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/maintenance_form.html', {'form': form})

@login_required
def maintenance_update(request, pk):
    maintenance = get_object_or_404(Maintenance, pk=pk)
    form = MaintenanceForm(request.POST or None, instance=maintenance)
    if form.is_valid():
        form.save()
        messages.success(request, 'Maintenance updated successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/maintenance_form.html', {'form': form})

@login_required
def maintenance_delete(request, pk):
    maintenance = get_object_or_404(Maintenance, pk=pk)
    if request.method == 'POST':
        maintenance.delete()
        messages.success(request, 'Maintenance deleted successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/maintenance_confirm_delete.html', {'maintenance': maintenance})

# ================= EMPLOYEE CRUD =================
@login_required
@user_passes_test(is_admin)
def employee_list(request):
    employees = Employee.objects.select_related('user').all()
    return render(request, 'd_autos_app/employee.html', {'employees': employees})

@login_required
@user_passes_test(is_admin)
def employee_create(request):
    credentials_data = None
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            generated_password = getattr(form, 'generated_password', None)
            
            if generated_password:
                credentials_data = {
                    'name': f'{form.cleaned_data["first_name"]} {form.cleaned_data["last_name"]}',
                    'email': form.cleaned_data["email"],
                    'password': generated_password
                }
                messages.success(request, f'Employee {credentials_data["name"]} added successfully!')
            
            # Create a new empty form for next entry
            form = EmployeeForm()
    else:
        form = EmployeeForm()
    
    return render(request, 'd_autos_app/employee_form.html', {
        'form': form,
        'credentials_data': credentials_data
    })

@login_required
@user_passes_test(is_admin)
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None, instance=employee)
    if form.is_valid():
        form.save()
        messages.success(request, 'Employee updated successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/employee_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('dashboard')
    return render(request, 'd_autos_app/employee_confirm_delete.html', {'employee': employee})

# ================= AUTHENTICATION =================
class LoginView(View):
    """Handle user login."""
    
    template_name = 'login.html'
    form_class = UserLoginForm
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request, data=request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user_type = form.cleaned_data.get('user_type')
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                # Verify user type
                if user_type == 'admin' and not user.is_admin:
                    messages.error(request, 'You are not authorized as an administrator.')
                    return render(request, self.template_name, {'form': form})
                
                if user_type == 'employee' and user.user_type != 'employee':
                    messages.error(request, 'You are not authorized as an employee.')
                    return render(request, self.template_name, {'form': form})
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        
        return render(request, self.template_name, {'form': form})

@login_required
@user_passes_test(is_admin)
def employee_reset_password(request, pk):
    """Reset employee password and show new credentials."""
    employee = get_object_or_404(Employee, pk=pk)
    
    # Generate new password using same logic as form
    first_name = employee.user.first_name.upper()
    name_part = first_name[:3] if len(first_name) >= 3 else first_name.ljust(3, 'X')
    
    # Generate 3 unique random digits
    digits = random.sample(range(10), 3)
    number_part = ''.join(map(str, digits))
    
    new_password = name_part + number_part
    
    # Update user password
    employee.user.set_password(new_password)
    employee.user.save()
    
    messages.success(
        request, 
        f'Password reset for {employee.user.first_name} {employee.user.last_name}. '
        f'New login credentials: Email: {employee.user.email}, Password: {new_password}'
    )
    
    return redirect('dashboard')

@login_required
def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')