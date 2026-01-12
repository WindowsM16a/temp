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

        # Redirect based on user type
        if request.user.is_admin and request.path == '/dashboard/':
            # Admin can stay on dashboard
            return None
        elif request.user.is_employee and request.path == '/dashboard/':
            # Employee should be redirected to employee dashboard, but since we have the view handle it, maybe not needed
            return None
        # For other paths, perhaps restrict access
        # For example, employees shouldn't access admin-only pages like employee_list
        if request.user.is_employee and request.path.startswith('/employees/'):
            return redirect('dashboard')
        # Add more restrictions as needed

        return None