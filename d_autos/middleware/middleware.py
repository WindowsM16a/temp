from django.shortcuts import redirect
from django.urls import reverse

class UserTypeMiddleware:
    """Middleware to check user type and redirect accordingly."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip for anonymous users
        if not request.user.is_authenticated:
            return None
        
        # Skip for logout view
        if request.path.startswith('/logout/'):
            return None
        
        # Admin trying to access employee dashboard
        if request.user.is_admin and request.path.startswith('/dashboard/employee'):
            return redirect('admin_dashboard')
        
        # Employee trying to access admin dashboard
        if request.user.is_employee and request.path.startswith('/dashboard/admin'):
            return redirect('employee_dashboard')
        
        return None