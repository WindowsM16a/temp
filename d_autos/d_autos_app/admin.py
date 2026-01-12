from django.contrib import admin
from .models import (
    Customer, Employee, Car,
    Rental, Payment, Reservation, Maintenance
)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'get_full_name', 'role', 'department', 'hire_date')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__email')
    list_filter = ('role', 'department', 'hire_date')
    
    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.short_description = 'Full Name'


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'plate_number', 'availability')
    list_filter = ('availability', 'brand')
    search_fields = ('plate_number',)


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('customer', 'car', 'rental_date', 'return_date', 'total_cost')
    list_filter = ('rental_date',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('rental', 'amount', 'payment_status', 'payment_date')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'car', 'start_date', 'end_date', 'reservation_status')


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('car', 'employee', 'scheduled_date', 'cost')
