from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard URLs
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/employee/', views.employee_dashboard_view, name='employee_dashboard'),

    # Authentication URLs
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_create, name='customer_add'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    # Car URLs
    path('cars/', views.car_list, name='car_list'),
    path('cars/add/', views.car_create, name='car_add'),
    path('cars/<int:pk>/edit/', views.car_update, name='car_edit'),
    path('cars/<int:pk>/delete/', views.car_delete, name='car_delete'),

    # Rental URLs
    path('rentals/', views.rental_list, name='rental_list'),
    path('rentals/add/', views.rental_create, name='rental_add'),
    path('rentals/<int:pk>/edit/', views.rental_update, name='rental_edit'),
    path('rentals/<int:pk>/delete/', views.rental_delete, name='rental_delete'),
    path('rentals/<int:pk>/return/', views.return_rental, name='return_rental'),

    # Payment URLs
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/add/', views.payment_create, name='payment_add'),
    path('payments/<int:pk>/edit/', views.payment_update, name='payment_edit'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),

    # Reservation URLs
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/add/', views.reservation_create, name='reservation_add'),
    path('reservations/<int:pk>/edit/', views.reservation_update, name='reservation_edit'),
    path('reservations/<int:pk>/delete/', views.reservation_delete, name='reservation_delete'),

    # Maintenance URLs
    path('maintenances/', views.maintenance_list, name='maintenance_list'),
    path('maintenances/add/', views.maintenance_create, name='maintenance_add'),
    path('maintenances/<int:pk>/edit/', views.maintenance_update, name='maintenance_edit'),
    path('maintenances/<int:pk>/delete/', views.maintenance_delete, name='maintenance_delete'),

    # Employee URLs (admin only)
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_add'),
    path('employees/<int:pk>/edit/', views.employee_update, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('employees/<int:pk>/reset-password/', views.employee_reset_password, name='employee_reset_password'),

    # Password Reset URLs (optional)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html',
             email_template_name='auth/password_reset_email.html',
             subject_template_name='auth/password_reset_subject.txt'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='auth/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='auth/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]