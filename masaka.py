import subprocess
import os
import sys
import venv

def check_and_install_django(env_path):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "show", "django"], env={'VIRTUAL_ENV': env_path})
        print("Django is already installed.")
    except subprocess.CalledProcessError:
        print("Django is not installed. Installing Django...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "django"], env={'VIRTUAL_ENV': env_path})
        print("Django has been installed.")

def create_and_activate_virtual_env(env_path):
    if not os.path.exists(env_path):
        print("Creating a virtual environment...")
        venv.create(env_path, with_pip=True)
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")
    print("Activating the virtual environment...")
    if os.name == 'nt':  # For Windows
        activate_script = os.path.join(env_path, "Scripts", "activate")
    else:  # For Unix or MacOS
        activate_script = os.path.join(env_path, "bin", "activate")
    subprocess.call(activate_script, shell=True)
    print("Virtual environment activated.")

# Django Project Setup
class DjangoProjectSetup:
    def __init__(self, project_name, apps):
        self.project_name = project_name
        self.apps = apps
        self.project_path = self.get_project_path()
        self.env_path = os.path.join(self.project_path, 'env')
        create_and_activate_virtual_env(self.env_path)
        check_and_install_django(self.env_path)
        self.project_full_path = self.create_django_project()

    def get_project_path(self):
        # Default project path in the user's Documents directory
        default_path = os.path.join(os.path.expanduser('~'), 'Documents', 'DjangoProjects')
        print(f"Default path for Django project is set to: {default_path}")
        print("Press Enter to use the default path or enter a new path:")

        # User input for custom path, if provided
        project_path = input().strip() or default_path

        # Validate and create the path if necessary
        if not os.path.exists(project_path):
            print(f"The path {project_path} does not exist. Creating it.")
            os.makedirs(project_path)
        elif not os.access(project_path, os.W_OK):
            raise PermissionError(f"The path {project_path} is not writable. Please choose a different location.")
        
        return project_path

    def create_django_project(self):
        # Create the Django project in the project path
        try:
            process = subprocess.run([sys.executable, "-m", "django-admin", "startproject", self.project_name, self.project_path], shell=True, env={'VIRTUAL_ENV': self.env_path})
            if process.returncode == 0:
                print(f"Django project '{self.project_name}' created successfully at {self.project_path}")
                return os.path.join(self.project_path, self.project_name)
            else:
                raise subprocess.CalledProcessError(process.returncode, 'django-admin startproject')
        except subprocess.CalledProcessError as e:
            print(f"Failed to create Django project. Error: {e}")
            sys.exit(1)

    def create_django_apps(self):
        # Create each app in the project directory
        for app in self.apps:
            try:
                process = subprocess.run([sys.executable, "-m", "django-admin", "startapp", app, self.project_full_path], shell=True, env={'VIRTUAL_ENV': self.env_path})
                if process.returncode == 0:
                    print(f"Django app '{app}' created successfully in the project '{self.project_name}'")
                else:
                    raise subprocess.CalledProcessError(process.returncode, 'django-admin startapp')
            except subprocess.CalledProcessError as e:
                print(f"Failed to create Django app: {app}. Error: {e}")
                sys.exit(1)

    def get_settings_path(self):
        # Path to the settings.py file in the Django project
        return os.path.join(self.project_full_path, self.project_name, 'settings.py')

    def configure_database_settings(self, db_engine, db_name, db_user, db_password, db_host, db_port):
        settings_path = self.get_settings_path()

        # Database configuration string
        db_config = (
            f"DATABASES = {{\n"
            f"    'default': {{\n"
            f"        'ENGINE': '{db_engine}',\n"
            f"        'NAME': '{db_name}',\n"
            f"        'USER': '{db_user}',\n"
            f"        'PASSWORD': '{db_password}',\n"
            f"        'HOST': '{db_host}',\n"
            f"        'PORT': '{db_port}',\n"
            f"    }}\n"
            f"}}\n"
        )

        with open(settings_path, 'a') as file:
            file.write('\n# Database configuration\n')
            file.write(db_config)

# App Path Manager
class AppPathManager:
    def __init__(self, project_full_path, apps):
        self.project_full_path = project_full_path
        self.apps = apps
        self.app_paths = self.create_app_paths_dict()

    def create_app_paths_dict(self):
        app_paths = {}
        for app in self.apps:
            app_path = os.path.join(self.project_full_path, app)
            app_paths[app] = app_path
        return app_paths

    def get_app_path(self, app_name):
        return self.app_paths.get(app_name, None)

    def get_file_path(self, app_name, file_name):
        app_path = self.get_app_path(app_name)
        if app_path:
            return os.path.join(app_path, file_name)
        return None

# File Generator
class FileGenerator:
    def create_file(self, file_path, content):
        with open(file_path, 'a') as file:
            file.write(content)

    def create_or_append_file(self, file_path, content):
        if os.path.exists(file_path):
            with open(file_path, 'a') as file:
                file.write(content)
        else:
            with open(file_path, 'w') as file:
                file.write(content)

# HTML Template Generator
class HTMLTemplateGenerator:
    def __init__(self, app_manager, file_generator):
        self.app_manager = app_manager
        self.file_generator = file_generator

    def generate_template(self, app_name, template_name, content):
        template_path = os.path.join(self.app_manager.get_app_path(app_name), 'templates', app_name, template_name)
        self.file_generator.create_file(template_path, content)

# App File Configurator
class AppFileConfigurator:
    def __init__(self, app_manager, file_generator, template_generator):
        self.app_manager = app_manager
        self.file_generator = file_generator
        self.template_generator = template_generator

    def edit_auth_app(self):
        self.edit_auth_app_models()
        self.edit_auth_app_views()
        self.edit_auth_app_forms()
        self.edit_auth_app_urls()
        self.create_login_template()
        self.create_logout_template()

    def edit_auth_app_models(self):
        app_name = 'auth_app'
        models_path = self.app_manager.get_file_path(app_name, 'models.py')
        if models_path:
            content = """
# Define user types
class UserType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

from django.contrib.auth.models import AbstractUser, Group

# User Custom Model
class CustomUser(AbstractUser):
    # Add any additional fields you need for your user model here
    # Example: profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    user_type = models.CharField(max_length=20, choices=[
        ('visitor', 'Visitor'),
        ('traverser', 'Traverser'),
        ('administrator', 'Administrator')
    ], default='visitor')

    def __str__(self):
        return self.username
"""
            self.file_generator.create_or_append_file(models_path, content)

    def edit_auth_app_views(self):
        app_name = 'auth_app'
        views_path = self.app_manager.get_file_path(app_name, 'views.py')
        if views_path:
            content = """
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from .forms import RegistrationForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group_name = request.POST.get('user_type')
            if group_name == 'visitor':
                user.groups.add(Group.objects.get(name='Visitor'))
            elif group_name == 'traverser':
                user.groups.add(Group.objects.get(name='Traverser'))
            elif group_name == 'administrator':
                user.groups.add(Group.objects.get(name='Administrator'))
            login(request, user)
            return redirect('home')  # Change 'home' to your desired URL after registration
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
"""
            self.file_generator.create_or_append_file(views_path, content)

    def edit_auth_app_forms(self):
        app_name = 'auth_app'
        forms_path = self.app_manager.get_file_path(app_name, 'forms.py')
        if forms_path:
            content = """
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserType

class RegistrationForm(UserCreationForm):
    user_type = forms.ModelChoiceField(queryset=UserType.objects.all(), empty_label=None, label='User Type')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'user_type')
"""
            self.file_generator.create_or_append_file(forms_path, content)

    def edit_auth_app_urls(self):
        app_name = 'auth_app'
        urls_path = self.app_manager.get_file_path(app_name, 'urls.py')
        if urls_path:
            content = """
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    # Add login view if not already defined
]
"""
            self.file_generator.create_or_append_file(urls_path, content)

    def create_login_template(self):
        app_name = 'auth_app'
        template_name = 'login.html'
        content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <!-- Add your CSS styles and Bootstrap CDN links here -->
</head>
<body>
    <div class="container">
        <h1>Login</h1>
        <form method="post">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""
        self.template_generator.generate_template(app_name, template_name, content)

    def create_logout_template(self):
        app_name = 'auth_app'
        template_name = 'logout.html'
        content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Logout</title>
    <!-- Add your CSS styles and Bootstrap CDN links here -->
</head>
<body>
    <div class="container">
        <h1>Logout</h1>
        <p>You have been logged out successfully.</p>
        <a href="{% url 'login' %}">Login again</a>
    </div>
</body>
</html>
"""
        self.template_generator.generate_template(app_name, template_name, content)

# Main function to run the script
def main():
    project_name = "taskforce"
    apps = ["auth_app", "task_manager", "project_manager", "health_tracker", 
            "mind_wellness", "time_tracker", "seo_tools", "communication", 
            "data_analysis", "shop_manager", "payment_processor", 
            "custom_software_dev", "lifestyle_consultancy", "user_groups_management", 
            "project_export_import", "project_title_level_system", 
            "priority_table_management"]

    # Setup Django Project
    setup = DjangoProjectSetup(project_name, apps)
    setup.create_django_apps()

    # Manage App Paths
    app_manager = AppPathManager(setup.project_full_path, apps)

    # Configure App Files
    file_generator = FileGenerator()
    template_generator = HTMLTemplateGenerator(app_manager, file_generator)
    configurator = AppFileConfigurator(app_manager, file_generator, template_generator)
    
    # Edit auth_app and create login/logout templates
    configurator.edit_auth_app()

    # Optional Database Configuration
    db_setup = input("Do you want to set up the database configuration now? (yes/no): ").strip().lower()
    if db_setup == 'yes':
        db_engine = input("Enter your database engine (e.g., 'django.db.backends.postgresql'): ").strip()
        db_name = input("Enter your database name: ").strip()
        db_user = input("Enter your database user: ").strip()
        db_password = input("Enter your database password: ").strip()
        db_host = input("Enter your database host: ").strip()
        db_port = input("Enter your database port: ").strip()
    elif db_setup == 'wdm':
        # Hardcoded database details for the 'wdm' input
        db_engine = 'django.db.backends.postgresql'
        db_name = 'wdmdatabase'
        db_user = 'atlas'  # Special case where the user title is 'atlas'
        db_password = 'Lightvessel100!'
        db_host = 'wdm-db.cihp8rwuaz6j.eu-north-1.rds.amazonaws.com'
        db_port = '5432'
    else:
        # Skip database configuration
        print("Skipping database configuration.")

    setup.configure_database_settings(db_engine, db_name, db_user, db_password, db_host, db_port)
    print("Database configuration has been updated.")

    print(f"Django project '{project_name}' created successfully at {setup.project_full_path}")


if __name__ == "__main__":
    main()

