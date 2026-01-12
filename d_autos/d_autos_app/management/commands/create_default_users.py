from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from d_autos_app.models import Employee

User = get_user_model()

class Command(BaseCommand):
    help = 'Create default admin and employee users'

    def handle(self, *args, **options):
        # Create default admin user
        if not User.objects.filter(email='admin@carrental.com').exists():
            admin_user = User.objects.create_user(
                email='admin@carrental.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                user_type='admin',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('Created default admin user: admin@carrental.com / admin123'))
        else:
            self.stdout.write('Admin user already exists')

        # Create default employee user
        if not User.objects.filter(email='employee@carrental.com').exists():
            employee_user = User.objects.create_user(
                email='employee@carrental.com',
                password='employee123',
                first_name='John',
                last_name='Doe',
                user_type='employee',
                phone='1234567890'
            )
            # Create employee profile
            Employee.objects.create(
                user=employee_user,
                role='sales_agent',
                hire_date='2024-01-01',
                salary=3000.00
            )
            self.stdout.write(self.style.SUCCESS('Created default employee user: employee@carrental.com / employee123'))
        else:
            self.stdout.write('Employee user already exists')