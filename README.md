# vigilant-guacamole

This is a Django web application, internally named "Rubik". It features user registration with admin approval, a user dashboard, and web search functionality.

## Setup and Installation

### Prerequisites
*   Python 3.8+
*   Pip (Python package installer)
*   Git

### Environment Variables
This project uses `python-decouple` to manage settings like `SECRET_KEY`, `DEBUG` mode, and `ALLOWED_HOSTS` via environment variables. You'll need to create a `.env` file in the project root directory (where `manage.py` is located).

1.  **Create a `.env` file:**
    ```bash
    touch .env
    ```
    (This file is listed in `.gitignore` and should not be committed to the repository.)

2.  **Populate `.env` with necessary variables:**
    ```env
    # Django Settings
    SECRET_KEY=your_very_secret_and_unique_django_secret_key_here # IMPORTANT: Generate a new strong key
    DJANGO_DEBUG=True # Set to False in production
    DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost # Comma-separated list of allowed hosts

    # Email Settings (for password reset, etc.)
    # For development, using the console backend (emails are printed to the console):
    EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
    #
    # For production, configure your actual SMTP settings:
    # EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    # EMAIL_HOST=your_smtp_server
    # EMAIL_PORT=587
    # EMAIL_USE_TLS=True
    # EMAIL_HOST_USER=your_email_address
    # EMAIL_HOST_PASSWORD=your_email_password
    # DEFAULT_FROM_EMAIL=your_default_from_address@example.com
    ```
    **Note:** For `SECRET_KEY`, you can generate one using Django's `get_random_secret_key()` function or an online generator. A good place to get a key is to run `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` in your shell.

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd vigilant-guacamole
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```

3.  **Install dependencies:**
    (Ensure your `.env` file is created with at least a `SECRET_KEY` before running pip install, as `settings.py` might be accessed by some packages during installation.)
    ```bash
    pip install -r requirements.txt
    ```
    (This will install Django, gunicorn, psycopg2-binary, googlesearch-python, python-decouple, Pillow, requests, beautifulsoup4)

4.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser (admin account):**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set up your admin username, email, and password.

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application should now be running at `http://127.0.0.1:8000/`. You can usually access the main page via `/accounts/` (or `/` if a root path is set up for `home`).

## Running Tests
To run the automated tests:
```bash
python manage.py test
```

## Key Features
*   User registration with email and username (requires admin approval).
*   Admin approval system for new users with search, sort, and pagination.
*   Separate dashboards for regular users and admin users.
*   Web search functionality for authenticated users, showing page titles and URLs with pagination.
*   User profile management (view and edit username, email, name, bio, profile picture).
*   Password reset functionality using email.
*   Configurable logging (console by default).
*   Environment-based settings for sensitive keys and debug mode.

## Project Structure
*   `rubik/`: Main Django project configuration.
    *   `settings.py`: Project settings (now configured with `python-decouple`).
    *   `urls.py`: Root URL configurations.
*   `accounts/`: Django app for user management, authentication, and core site logic.
    *   `models.py`: User-related database models.
    *   `views.py`: Request handling logic.
    *   `forms.py`: User registration and other forms.
    *   `urls.py`: App-specific URL configurations.
*   `templates/`: HTML templates.
    *   `base.html`: Base template for all pages.
*   `static/`: Static files (CSS, JavaScript, images).
*   `manage.py`: Django's command-line utility.
*   `requirements.txt`: Project dependencies.
*   `.env`: (You create this locally) Stores environment variables for configuration.
*   `.gitignore`: Specifies intentionally untracked files that Git should ignore.