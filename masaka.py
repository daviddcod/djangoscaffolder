import subprocess
import os
import sys
import venv
import ctypes

def run_batch_script_and_wait(script_path):
    # Run the batch script and wait for it to complete
    process = subprocess.Popen(script_path, shell=True)
    process.wait()

def create_virtual_env(env_path):
    if not os.path.exists(env_path):
        print("Creating a virtual environment...")
        venv.create(env_path, with_pip=True)
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")

def create_setup_script(env_path, project_path, project_name, apps):
    activate_script = os.path.join(env_path, "Scripts", "activate.bat") if os.name == 'nt' else os.path.join(env_path, "bin", "activate")
    setup_script_path = os.path.join(project_path, "setup_django.bat")

    with open(setup_script_path, 'w') as file:
        file.write(f'@echo off\n')
        file.write(f'cd /d "{project_path}"\n')
        file.write(f'call "{activate_script}"\n')
        file.write(f'pip install django\n')
        file.write(f'pip install psycopg2\n')  # Install psycopg2
        file.write(f'django-admin startproject {project_name} .\n')

        for app in apps:
            file.write(f'django-admin startapp {app}\n')

    return setup_script_path

class DjangoProjectSetup:
    def __init__(self, project_name, apps):
        self.project_name = project_name
        self.apps = apps
        self.project_path = self.get_project_path()
        self.env_path = os.path.join(self.project_path, 'env')
        create_virtual_env(self.env_path)
        self.project_full_path = self.project_path
        self.create_and_run_setup_script()

    def get_project_path(self):
        default_path = os.path.join(os.path.expanduser("~"), 'DjangoProjects', self.project_name)
        print(f"Default path for Django project is set to: {default_path}")
        if not os.path.exists(default_path):
            print(f"The path {default_path} does not exist. Creating it.")
            os.makedirs(default_path)
        return default_path

    def create_and_run_setup_script(self):
        setup_script = create_setup_script(self.env_path, self.project_path, self.project_name, self.apps)
        run_batch_script_and_wait(setup_script)

    def check_and_install_django(self):
        activate_script = os.path.join(self.env_path, "Scripts", "activate") if os.name == 'nt' else os.path.join(self.env_path, "bin", "activate")
        install_command = f'{activate_script} && {sys.executable} -m pip install django'
        subprocess.run(install_command, shell=True)
        # Check if Django is installed
        try:
            subprocess.check_call(f'{activate_script} && {sys.executable} -m django --version', shell=True)
            print("Django installed successfully.")
        except subprocess.CalledProcessError:
            print("Django installation failed.")
            sys.exit(1)

    def create_django_project(self):
        django_admin_path = os.path.join(self.env_path, "Scripts", "django-admin.py") if os.name == 'nt' else os.path.join(self.env_path, "bin", "django-admin.py")
        command = f'{sys.executable} {django_admin_path} startproject {self.project_name} {self.project_path}'
        subprocess.run(command, shell=True)
        return os.path.join(self.project_path, self.project_name)

    def create_django_apps(self):
        django_admin_path = os.path.join(self.env_path, "Scripts", "django-admin.py") if os.name == 'nt' else os.path.join(self.env_path, "bin", "django-admin.py")
        for app in self.apps:
            app_path = os.path.join(self.project_full_path, app)
            if not os.path.exists(app_path):
                os.makedirs(app_path)
            command = f'{sys.executable} {django_admin_path} startapp {app} {app_path}'
            subprocess.run(command, shell=True)
            
    def configure_settings(self, db_engine, db_name, db_user, db_password, db_host, db_port, apps):
        settings_path = os.path.join(self.project_path, self.project_name, 'settings.py')

        # Read the current content of settings.py
        with open(settings_path, 'r') as file:
            settings_content = file.readlines()

        # Prepare the new database configuration
        new_db_config = (
            "AUTH_USER_MODEL = 'auth_app.CustomUser'\n"  # Set custom user model
            "DATABASES = {\n"
            "    'default': {\n"
            f"        'ENGINE': '{db_engine}',\n"
            f"        'NAME': '{db_name}',\n"
            f"        'USER': '{db_user}',\n"
            f"        'PASSWORD': '{db_password}',\n"
            f"        'HOST': '{db_host}',\n"
            f"        'PORT': '{db_port}',\n"
            "    }\n"
        )

        # Find and replace the existing DATABASES definition
        new_settings_content = []
        db_section_found = False
        for line in settings_content:
            if line.strip().startswith('DATABASES = {'):
                new_settings_content.append(new_db_config)
                db_section_found = True
            elif db_section_found and line.strip() == '}':
                db_section_found = False
            elif not db_section_found:
                new_settings_content.append(line)

        # Add all apps to INSTALLED_APPS
        installed_apps_index = next(i for i, line in enumerate(new_settings_content) if 'INSTALLED_APPS' in line)
        for app in apps:
            new_settings_content.insert(installed_apps_index + 1, f"    '{app}',\n")
            installed_apps_index += 1

        # Write the modified settings back to the file
        with open(settings_path, 'w') as file:
            file.writelines(new_settings_content)

class AppPathManager:
    def __init__(self,project_full_path , project_name, apps):
        self.project_name = project_name
        self.apps = apps
        self.project_full_path = project_full_path
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

class HTMLTemplateGenerator:
    def __init__(self, app_manager, file_generator):
        self.app_manager = app_manager
        self.file_generator = file_generator

    def generate_template(self, app_name, template_name, content):
        template_directory = os.path.join(self.app_manager.get_app_path(app_name), 'templates', app_name)
        os.makedirs(template_directory, exist_ok=True)  # Create the template directory if it doesn't exist
        template_path = os.path.join(template_directory, template_name)
        self.file_generator.create_file(template_path, content)

class AppFileEditor:
    def __init__(self, app_manager, file_generator, template_generator):
        self.app_manager = app_manager
        self.file_generator = file_generator
        self.template_generator = template_generator

    def edit_models(self, app_name, model_content):
        models_path = self.app_manager.get_file_path(app_name, 'models.py')
        if models_path:
            self.file_generator.create_or_append_file(models_path, model_content)

    def edit_views(self, app_name, views_content):
        views_path = self.app_manager.get_file_path(app_name, 'views.py')
        if views_path:
            self.file_generator.create_or_append_file(views_path, views_content)

    def edit_templates(self, app_name, template_name, template_content):
        self.template_generator.generate_template(app_name, template_name, template_content)

    def edit_forms(self, app_name, forms_content):
        forms_path = self.app_manager.get_file_path(app_name, 'forms.py')
        if forms_path:
            self.file_generator.create_or_append_file(forms_path, forms_content)

class AppFileConfigurator:
    def __init__(self, setup, app_manager, file_editor):
        self.setup = setup
        self.app_manager = app_manager
        self.file_editor = file_editor
        self.generated_views = {}  # Track generated views for each app

    def configure_app(self, app_name):
        # Initialize an entry for the app in self.generated_views
        self.generated_views[app_name] = {}

        # Define methods to configure models, views, templates, etc. for each app
        if app_name == 'auth_app':
            self.configure_auth_app(app_name)
        # Add more conditions for other apps as needed

    def configure_auth_app(self, app_name):
        # Define the content for models.py
        models_content = """
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

# Define user types
class UserType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

# User Custom Model
class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=20, choices=[
        ('visitor', 'Visitor'),
        ('traverser', 'Traverser'),
        ('administrator', 'Administrator')
    ], default='visitor')

    # Adding related_name to avoid clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='customuser_set',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='customuser_set',
        related_query_name='customuser',
    )

    def __str__(self):
        return self.username
        """
        # Define the content for views.py
 
        views_content = """
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'auth_app/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('auth_app_home')
    else:
        form = LoginForm()
    return render(request, 'auth_app/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('auth_app_logout')

@login_required(login_url='register')
def home(request):
    return render(request, 'auth_app/home.html')
        """

        # Define the content for forms.py
        forms_content = """
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
        """

        # HTML content for login, logout, register, and home templates
        templates_content = {
            'login.html': """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <title>Login</title>
</head>
<body>
    <div class="container mt-5">
        <h1>Login</h1>
        <form method="post" class="mt-3">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-primary">Login</button>
        </form>
    </div>
</body>
</html>
            """,
            'logout.html': """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <title>Logout</title>
</head>
<body>
    <div class="container mt-5">
        <h1>Logout</h1>
        <p>You have been logged out successfully.</p>
        <a href="{% url 'login' %}" class="btn btn-primary">Login again</a>
    </div>
</body>
</html>
            """,
            'register.html': """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <title>Register</title>
</head>
<body>
    <div class="container mt-5">
        <h1>Register</h1>
        <form method="post" class="mt-3">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-primary">Register</button>
        </form>
    </div>
</body>
</html>
            """,
            'home.html': """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <title>Home</title>
</head>
<body>
    <div class="container">
        <h1>Welcome to the Home Page</h1>
        <p>This is the main page of the application, accessible only to logged-in users.</p>
    </div>
</body>
</html>
            """
        }

        # Apply the content to the respective files
        self.file_editor.edit_models(app_name, models_content)
        self.file_editor.edit_views(app_name, views_content)
        self.file_editor.edit_forms(app_name, forms_content)

        for template_name, template_content in templates_content.items():
            self.file_editor.edit_templates(app_name, template_name, template_content)

        # Update generated views for URL configuration
        self.generated_views[app_name] = {
            'register': 'auth_app/register.html',
            'user_login': 'auth_app/login.html',
            'user_logout': 'auth_app/logout.html',
            'home': 'auth_app/home.html'
        }
    
    def apply_migrations(self):
        # Run makemigrations and migrate commands
        activate_script = os.path.join(self.setup.env_path, "Scripts", "activate") if os.name == 'nt' else os.path.join(self.setup.env_path, "bin", "activate")
        makemigrations_command = f'{activate_script} && cd {self.setup.project_full_path} && python manage.py makemigrations'
        migrate_command = f'{activate_script} && cd {self.setup.project_full_path} && python manage.py migrate'
        
        try:
            subprocess.run(makemigrations_command, shell=True, check=True)
            subprocess.run(migrate_command, shell=True, check=True)
            print("Database migrations applied successfully.")
        except subprocess.CalledProcessError:
            print("Error applying database migrations.")
            sys.exit(1)

    def update_main_urls(self):
        main_urls_path = os.path.join(self.setup.project_full_path, self.setup.project_name, 'urls.py')

        try:
            with open(main_urls_path, 'r+') as file:
                existing_content = file.read()

                # Split the existing content into two parts: before and after urlpatterns
                if "urlpatterns = [" in existing_content:
                    parts = existing_content.split("urlpatterns = [")
                    header = parts[0]  # Content before 'urlpatterns = ['
                    urlpatterns_section = "urlpatterns = [" + parts[1]
                else:
                    header = existing_content
                    urlpatterns_section = "urlpatterns = [\n    path('admin/', admin.site.urls),\n"

                # Process the header to add necessary imports
                import_lines = ""
                for app_name, views in self.generated_views.items():
                    if views:  # Check if there are any views generated for the app
                        import_line = f"from {app_name} import views as {app_name}_views\n"
                        if import_line not in header:  # Avoid duplicate imports
                            import_lines += import_line

                # Process the urlpatterns section to add URL patterns
                urlpatterns_content, closing = urlpatterns_section.rsplit("]", 1)
                for app_name, views in self.generated_views.items():
                    for view_name in views:
                        url_pattern = f"    path('{app_name}/{view_name}/', {app_name}_views.{view_name}, name='{app_name}_{view_name}'),\n"
                        if url_pattern not in urlpatterns_content:  # Avoid duplicate patterns
                            urlpatterns_content += url_pattern

                # Combine the parts and write back to the file
                final_content = import_lines + header + urlpatterns_content + "]" + closing
                file.seek(0)
                file.write(final_content)
                file.truncate()

        except Exception as e:
            print(f"Error updating URLs: {e}")  # Error handling
        
def main():
    project_name = "taskforce"
    apps = ["auth_app", "task_manager", "project_manager", "health_tracker", 
            "mind_wellness", "time_tracker", "seo_tools", "communication", 
            "data_analysis", "shop_manager", "payment_processor", 
            "custom_software_dev", "lifestyle_consultancy", "user_groups_management", 
            "project_export_import", "project_title_level_system", 
            "priority_table_management"]

    setup = DjangoProjectSetup(project_name, apps)
    

    # Configure database settings after the Django project setup is complete
    # db_engine = 'django.db.backends.postgresql'
    # db_name = 'db_name'
    # db_user = 'db_user'
    # db_password = 'db_password!'
    # db_host = 'wdm-db.cihp8rwuaz6j.eu-north-1.rds.amazonaws.com < reccomended'
    # db_port = '5432'

    #setup.configure_settings(db_engine, db_name, db_user, db_password, db_host, db_port, apps)
    # print("Database configuration has been updated.")

    app_manager = AppPathManager(setup.project_full_path, setup.project_name, apps)  # Pass project_name here
    file_generator = FileGenerator()
    template_generator = HTMLTemplateGenerator(app_manager, file_generator)
    file_editor = AppFileEditor(app_manager, file_generator, template_generator)
    configurator = AppFileConfigurator(setup, app_manager, file_editor)

    for app in apps:
        configurator.configure_app(app)

    # Update main urls.py for all apps and views
    configurator.update_main_urls()

    # Apply database migrations
    configurator.apply_migrations()

    print(f"Django project '{project_name}' created successfully at {setup.project_full_path}")

    # Optional: Launch Django development server
    if setup is not None:
        activate_script = os.path.join(setup.project_full_path, "env", "Scripts", "activate") if os.name == 'nt' else os.path.join(setup.project_full_path, "env", "bin", "activate")
        cmd_command = f'cmd /k {activate_script} && cd {setup.project_full_path} && python manage.py runserver'
        subprocess.Popen(cmd_command, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

if __name__ == "__main__":
    main()
